import os
import logging
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from database_enhanced import get_db
from auth_utils import get_current_user
from models import User, Streak, StreakLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/streaks", tags=["Streaks"])

@router.get("/")
async def test_streak():
    """Test endpoint to verify streak routes are working"""
    return {"message": "Streak routes are working!"}

@router.get("/page", response_class=HTMLResponse)
async def streaks_page(request: Request):
    """Display the streaks page with calendar"""
    return templates.TemplateResponse("streaks.html", {
        "request": request
    })

@router.get("/demo", response_class=HTMLResponse)
async def streaks_demo_page(request: Request):
    """Display the streaks demo page"""
    return templates.TemplateResponse("streaks_demo.html", {
        "request": request
    })

# Get templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.post("/log-activity")
async def log_activity(
    activity_type: str,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a new activity and update streak"""
    try:
        today = date.today()
        
        # Check if activity already logged today
        existing_log = db.query(StreakLog).filter(
            and_(
                StreakLog.user_id == current_user.id,
                StreakLog.activity_type == activity_type,
                func.date(StreakLog.activity_date) == today
            )
        ).first()
        
        if existing_log:
            return JSONResponse(
                status_code=400,
                content={"message": "Activity already logged for today"}
            )
        
        # Create new activity log
        new_log = StreakLog(
            user_id=current_user.id,
            activity_type=activity_type,
            description=description
        )
        db.add(new_log)
        
        # Get or create streak record
        streak = db.query(Streak).filter(
            and_(
                Streak.user_id == current_user.id,
                Streak.activity_type == activity_type
            )
        ).first()
        
        if not streak:
            streak = Streak(
                user_id=current_user.id,
                activity_type=activity_type,
                current_streak=1,
                longest_streak=1,
                last_activity_date=datetime.now()
            )
            db.add(streak)
        else:
            # Check if this is consecutive day
            if streak.last_activity_date:
                last_date = streak.last_activity_date.date()
                if today - last_date == timedelta(days=1):
                    # Consecutive day - increment streak
                    streak.current_streak += 1
                    if streak.current_streak > streak.longest_streak:
                        streak.longest_streak = streak.current_streak
                elif today - last_date > timedelta(days=1):
                    # Gap in streak - reset to 1
                    streak.current_streak = 1
                # If same day, streak remains the same
            else:
                # First activity
                streak.current_streak = 1
                streak.longest_streak = 1
            
            streak.last_activity_date = datetime.now()
        
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Activity logged successfully",
                "current_streak": streak.current_streak,
                "longest_streak": streak.longest_streak
            }
        )
        
    except Exception as e:
        logger.error(f"Error logging activity: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/get-streaks")
async def get_streaks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all streaks for the current user"""
    try:
        streaks = db.query(Streak).filter(
            Streak.user_id == current_user.id
        ).all()
        
        return JSONResponse(
            status_code=200,
            content={
                "streaks": [streak.to_dict() for streak in streaks]
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting streaks: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/get-calendar-data")
async def get_calendar_data(
    activity_type: str = "general",
    year: int = None,
    month: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar data for streak visualization"""
    try:
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        # Get start and end of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Get all activity logs for the month
        logs = db.query(StreakLog).filter(
            and_(
                StreakLog.user_id == current_user.id,
                StreakLog.activity_type == activity_type,
                StreakLog.activity_date >= start_date,
                StreakLog.activity_date <= end_date
            )
        ).all()
        
        # Create calendar data
        calendar_data = {}
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            calendar_data[date_key] = {
                "date": date_key,
                "day": current_date.day,
                "has_activity": False,
                "streak_count": 0
            }
            current_date += timedelta(days=1)
        
        # Mark days with activity
        for log in logs:
            date_key = log.activity_date.strftime("%Y-%m-%d")
            if date_key in calendar_data:
                calendar_data[date_key]["has_activity"] = True
        
        # Calculate streak counts for each day
        streak_count = 0
        for date_key in sorted(calendar_data.keys()):
            if calendar_data[date_key]["has_activity"]:
                streak_count += 1
            else:
                streak_count = 0
            calendar_data[date_key]["streak_count"] = streak_count
        
        return JSONResponse(
            status_code=200,
            content={
                "calendar_data": list(calendar_data.values()),
                "year": year,
                "month": month,
                "month_name": start_date.strftime("%B")
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting calendar data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/get-streak-stats")
async def get_streak_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall streak statistics"""
    try:
        # Get all streaks
        streaks = db.query(Streak).filter(
            Streak.user_id == current_user.id
        ).all()
        
        # Calculate total stats
        total_current_streak = sum(s.current_streak for s in streaks)
        total_longest_streak = sum(s.longest_streak for s in streaks)
        total_activities = len(streaks)
        
        # Get today's activities
        today = date.today()
        today_activities = db.query(StreakLog).filter(
            and_(
                StreakLog.user_id == current_user.id,
                func.date(StreakLog.activity_date) == today
            )
        ).count()
        
        # Get user's last login date
        last_login_date = current_user.last_login.isoformat() if current_user.last_login else None
        
        return JSONResponse(
            status_code=200,
            content={
                "total_current_streak": total_current_streak,
                "total_longest_streak": total_longest_streak,
                "total_activities": total_activities,
                "today_activities": today_activities,
                "last_login_date": last_login_date,
                "streaks": [streak.to_dict() for streak in streaks]
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting streak stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/update-last-login")
async def update_last_login(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's last login date"""
    try:
        # Update the user's last login date
        current_user.last_login = datetime.now()
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Last login updated successfully",
                "last_login": current_user.last_login.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating last login: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
