import os
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database_enhanced import get_db
from auth_utils import get_current_user
from models import User, Post, Connection, Comment, Job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["Home"])

# Test route to verify router is working
@router.get("/test")
async def test_home_router():
    """Test route to verify home router is working"""
    return {"message": "Home router is working!"}

# Get templates (legacy) and SPA dist path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "fronted", "dist", "public")

def get_analytics_data(db: Session, user_id: int):
    """Get comprehensive analytics data for the user's network"""
    try:
        # Get user's connections
        connections = db.query(Connection).filter(
            (Connection.user_id == user_id) | (Connection.connected_user_id == user_id)
        ).filter(Connection.status == 'accepted').all()
        
        # Get connected user IDs
        connected_user_ids = set()
        for conn in connections:
            if conn.user_id == user_id:
                connected_user_ids.add(conn.connected_user_id)
            else:
                connected_user_ids.add(conn.user_id)
        
        # Get network statistics
        network_stats = {
            'total_connections': len(connections),
            'active_connections': len([c for c in connections if c.status == 'accepted']),
            'pending_connections': len([c for c in connections if c.status == 'pending']),
            'total_network_users': len(connected_user_ids) + 1  # +1 for current user
        }
        
        # Get posts from network (user + connections)
        network_posts = db.query(Post).filter(
            Post.user_id.in_(list(connected_user_ids) + [user_id])
        ).order_by(Post.created_at.desc()).limit(50).all()
        
        # Get top performing posts from network
        top_posts = []
        for post in network_posts[:10]:
            # Calculate engagement (likes + comments)
            engagement = 0
            if hasattr(post, 'likes'):
                engagement += len(post.likes) if post.likes else 0
            if hasattr(post, 'comments'):
                engagement += len(post.comments) if post.comments else 0
            
            top_posts.append({
                'id': post.id,
                'content': post.content[:100] + "..." if len(post.content) > 100 else post.content,
                'user_name': post.user.full_name if post.user else "Unknown User",
                'engagement': engagement,
                'created_at': post.created_at
            })
        
        # Sort by engagement
        top_posts.sort(key=lambda x: x['engagement'], reverse=True)
        
        # Get network activity insights
        network_insights = {
            'new_connections_this_week': len([c for c in connections if c.created_at and (datetime.now() - c.created_at).days <= 7]),
            'active_posts_this_week': len([p for p in network_posts if p.created_at and (datetime.now() - p.created_at).days <= 7]),
            'total_network_posts': len(network_posts),
            'network_growth_rate': calculate_growth_rate(db, user_id, connections)
        }
        
        # Get connection growth data (last 12 months)
        connection_growth = get_connection_growth_data(db, user_id)
        
        # Get profile views trend (simulated data for now)
        profile_views_trend = get_profile_views_trend()
        
        # Get network demographics
        network_demographics = get_network_demographics(db, connected_user_ids)
        
        return {
            'network_stats': network_stats,
            'top_posts': top_posts[:5],  # Top 5 posts
            'network_insights': network_insights,
            'connection_growth': connection_growth,
            'profile_views_trend': profile_views_trend,
            'network_demographics': network_demographics
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics data: {e}")
        return get_default_analytics_data()

def get_connection_growth_data(db: Session, user_id: int):
    """Get connection growth data over time"""
    try:
        # Get connections created in the last 12 months
        from datetime import datetime, timedelta
        twelve_months_ago = datetime.now() - timedelta(days=365)
        
        connections = db.query(Connection).filter(
            (Connection.user_id == user_id) | (Connection.connected_user_id == user_id)
        ).filter(Connection.status == 'accepted').filter(Connection.created_at >= twelve_months_ago).all()
        
        # Group by month
        monthly_data = {}
        for conn in connections:
            month_key = conn.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += 1
        
        # Generate last 12 months data
        growth_data = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            month_key = date.strftime('%Y-%m')
            count = monthly_data.get(month_key, 0)
            growth_data.append({
                'month': date.strftime('%b'),
                'count': count
            })
        
        growth_data.reverse()  # Oldest to newest
        return growth_data
        
    except Exception as e:
        logger.error(f"Error getting connection growth data: {e}")
        return get_default_growth_data()

def get_profile_views_trend():
    """Get profile views trend data (simulated for now)"""
    # This would typically come from a profile views tracking system
    return [
        {'day': 'Mon', 'views': 65},
        {'day': 'Tue', 'views': 89},
        {'day': 'Wed', 'views': 120},
        {'day': 'Thu', 'views': 156},
        {'day': 'Fri', 'views': 98},
        {'day': 'Sat', 'views': 145},
        {'day': 'Sun', 'views': 178}
    ]

def get_network_demographics(db: Session, connected_user_ids: set):
    """Get demographics of user's network"""
    try:
        if not connected_user_ids:
            return {'total_users': 0, 'professionals': 0, 'students': 0, 'companies': 0}
        
        users = db.query(User).filter(User.id.in_(list(connected_user_ids))).all()
        
        demographics = {
            'total_users': len(users),
            'professionals': len([u for u in users if u.user_type == 'professional']),
            'students': len([u for u in users if u.user_type == 'student']),
            'companies': len([u for u in users if u.user_type == 'company'])
        }
        
        return demographics
        
    except Exception as e:
        logger.error(f"Error getting network demographics: {e}")
        return {'total_users': 0, 'professionals': 0, 'students': 0, 'companies': 0}

def calculate_growth_rate(db: Session, user_id: int, connections: list):
    """Calculate network growth rate"""
    try:
        if not connections:
            return 0
        
        # Get connections from last month vs previous month
        from datetime import datetime, timedelta
        one_month_ago = datetime.now() - timedelta(days=30)
        two_months_ago = datetime.now() - timedelta(days=60)
        
        recent_connections = len([c for c in connections if c.created_at and c.created_at >= one_month_ago])
        previous_connections = len([c for c in connections if c.created_at and c.created_at >= two_months_ago and c.created_at < one_month_ago])
        
        if previous_connections == 0:
            return recent_connections * 100
        
        growth_rate = ((recent_connections - previous_connections) / previous_connections) * 100
        return round(growth_rate, 1)
        
    except Exception as e:
        logger.error(f"Error calculating growth rate: {e}")
        return 0

def get_default_analytics_data():
    """Return default analytics data if there's an error"""
    return {
        'network_stats': {'total_connections': 0, 'active_connections': 0, 'pending_connections': 0, 'total_network_users': 0},
        'top_posts': [],
        'network_insights': {'new_connections_this_week': 0, 'active_posts_this_week': 0, 'total_network_posts': 0, 'network_growth_rate': 0},
        'connection_growth': get_default_growth_data(),
        'profile_views_trend': get_profile_views_trend(),
        'network_demographics': {'total_users': 0, 'professionals': 0, 'students': 0, 'companies': 0}
    }

def get_default_growth_data():
    """Return default growth data"""
    return [
        {'month': 'Jan', 'count': 0},
        {'month': 'Feb', 'count': 0},
        {'month': 'Mar', 'count': 0},
        {'month': 'Apr', 'count': 0},
        {'month': 'May', 'count': 0},
        {'month': 'Jun', 'count': 0},
        {'month': 'Jul', 'count': 0},
        {'month': 'Aug', 'count': 0},
        {'month': 'Sep', 'count': 0},
        {'month': 'Oct', 'count': 0},
        {'month': 'Nov', 'count': 0},
        {'month': 'Dec', 'count': 0}
    ]

@router.get("/home", response_class=HTMLResponse)
async def home_page():
    """Serve SPA for home route"""
    index_path = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="http://localhost:5000/home", status_code=307)

@router.post("/update-profile")
async def update_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        form_data = await request.form()
        
        # Update user fields
        if 'full_name' in form_data:
            current_user.full_name = form_data['full_name']
        
        if 'title' in form_data:
            current_user.title = form_data['title']
        
        if 'company' in form_data:
            current_user.company = form_data['company']
        
        if 'location' in form_data:
            current_user.location = form_data['location']
        
        if 'experience_years' in form_data:
            try:
                current_user.experience_years = int(form_data['experience_years'])
            except ValueError:
                current_user.experience_years = 0
        
        if 'bio' in form_data:
            current_user.bio = form_data['bio']
        
        if 'skills' in form_data:
            current_user.skills = form_data['skills']
        
        if 'interests' in form_data:
            current_user.interests = form_data['interests']
        
        if 'education' in form_data:
            current_user.education = form_data['education']
        
        if 'profile_visibility' in form_data:
            current_user.profile_visibility = form_data['profile_visibility']
        
        if 'show_email' in form_data:
            current_user.show_email = form_data['show_email'] == 'true'
        
        if 'show_phone' in form_data:
            current_user.show_phone = form_data['show_phone'] == 'true'
        
        # Save changes
        db.commit()
        
        return {"success": True, "message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating profile"
        )

@router.get("/profile/{user_id:int}")
async def get_user_profile(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a user's public profile"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if profile is visible to current user
        if user.profile_visibility == 'private' and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This profile is private"
            )
        
        # Get user's connections
        connections = db.query(Connection).filter(
            (Connection.user_id == user_id) | (Connection.connected_user_id == user_id)
        ).filter(Connection.status == 'accepted').count()
        
        # Get user's posts count
        post_count = db.query(Post).filter(Post.user_id == user_id).count()
        
        return templates.TemplateResponse("profile_view.html", {
            "request": request,
            "profile_user": user,
            "current_user": current_user,
            "connection_count": connections,
            "post_count": post_count
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting profile"
        )

@router.get("/debug-hr", response_class=HTMLResponse)
async def debug_hr_page(request: Request, current_user: User = Depends(get_current_user)):
    """Debug page to troubleshoot HR dashboard button visibility"""
    return templates.TemplateResponse("debug_hr.html", {
        "request": request,
        "user": current_user
    })

@router.get("/debug/jobs", response_class=JSONResponse)
async def debug_jobs(
    request: Request,
    db: Session = Depends(get_db)
):
    """Debug route to check jobs in database"""
    try:
        # Get all jobs
        jobs = db.query(Job).all()
        
        # Get job applications
        applications = db.query(JobApplication).all()
        
        return {
            "total_jobs": len(jobs),
            "active_jobs": len([j for j in jobs if j.is_active]),
            "total_applications": len(applications),
            "jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "is_active": job.is_active,
                    "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                    "posted_by": job.posted_by
                }
                for job in jobs
            ],
            "applications": [
                {
                    "id": app.id,
                    "job_id": app.job_id,
                    "applicant_id": app.applicant_id,
                    "status": app.status
                }
                for app in applications
            ]
        }
    except Exception as e:
        logger.error(f"Error in debug route: {e}")
        return {"error": str(e)}

# ==================== JOB APPLICATIONS ====================





@router.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    import os
    
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.svg")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/svg+xml")
    else:
        # Return a simple response if favicon doesn't exist
        from fastapi.responses import Response
        return Response(content="", media_type="image/svg+xml")





