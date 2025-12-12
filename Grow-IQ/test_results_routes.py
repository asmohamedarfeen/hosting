import os
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from database import get_db
from auth_utils import get_current_user
from models import User, MockInterviewSession, ResumeTestResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/test-results", tags=["Test Results"])

# ========== MOCK INTERVIEW RESULTS ==========

@router.get("/mock-interviews/{user_id}")
async def get_user_mock_interviews(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all mock interview results for a specific user"""
    try:
        # Check if user is requesting their own results or is an HR user
        if current_user.id != user_id and not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="Access denied")
        
        interviews = db.query(MockInterviewSession).filter(
            MockInterviewSession.user_id == user_id
        ).order_by(desc(MockInterviewSession.started_at)).all()
        
        return JSONResponse(content={
            "success": True,
            "data": [interview.to_dict() for interview in interviews],
            "count": len(interviews)
        })
        
    except Exception as e:
        logger.error(f"Error fetching mock interview results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/mock-interviews/session/{session_uuid}")
async def get_mock_interview_session(
    session_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed results for a specific mock interview session"""
    try:
        session = db.query(MockInterviewSession).filter(
            MockInterviewSession.session_uuid == session_uuid
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check access permissions
        if current_user.id != session.user_id and not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="Access denied")
        
        return JSONResponse(content={
            "success": True,
            "data": session.to_dict()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching mock interview session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/mock-interviews/analytics/{user_id}")
async def get_mock_interview_analytics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics and statistics for mock interviews"""
    try:
        # Check access permissions
        if current_user.id != user_id and not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="Access denied")
        
        interviews = db.query(MockInterviewSession).filter(
            MockInterviewSession.user_id == user_id
        ).all()
        
        if not interviews:
            return JSONResponse(content={
                "success": True,
                "data": {
                    "total_sessions": 0,
                    "average_score": 0,
                    "best_score": 0,
                    "improvement_trend": [],
                    "grade_distribution": {},
                    "total_duration": 0
                }
            })
        
        # Calculate analytics
        total_sessions = len(interviews)
        scores = [i.score_overall for i in interviews if i.score_overall is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        
        # Grade distribution
        grade_distribution = {}
        for interview in interviews:
            grade = interview.overall_grade
            if grade:
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # Total duration
        total_duration = sum([i.interview_duration_minutes or 0 for i in interviews])
        
        # Improvement trend (last 5 sessions)
        recent_sessions = sorted(interviews, key=lambda x: x.started_at, reverse=True)[:5]
        improvement_trend = [s.score_overall for s in recent_sessions if s.score_overall is not None]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "total_sessions": total_sessions,
                "average_score": round(average_score, 2),
                "best_score": best_score,
                "improvement_trend": improvement_trend,
                "grade_distribution": grade_distribution,
                "total_duration": total_duration
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching mock interview analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== RESUME TEST RESULTS ==========

@router.get("/resume-tests/{user_id}")
async def get_user_resume_tests(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all resume test results for a specific user"""
    try:
        # Check access permissions
        if current_user.id != user_id and not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="Access denied")
        
        resume_tests = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == user_id
        ).order_by(desc(ResumeTestResult.analysis_timestamp)).all()
        
        return JSONResponse(content={
            "success": True,
            "data": [test.to_dict() for test in resume_tests],
            "count": len(resume_tests)
        })
        
    except Exception as e:
        logger.error(f"Error fetching resume test results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/resume-tests/result/{result_id}")
async def get_resume_test_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed results for a specific resume test"""
    try:
        result = db.query(ResumeTestResult).filter(
            ResumeTestResult.id == result_id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Check access permissions
        if current_user.id != result.user_id and not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="Access denied")
        
        return JSONResponse(content={
            "success": True,
            "data": result.to_dict()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching resume test result: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/resume-tests/analytics/{user_id}")
async def get_resume_test_analytics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics and statistics for resume tests"""
    try:
        # Check access permissions
        if current_user.id != user_id and not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="Access denied")
        
        resume_tests = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == user_id
        ).all()
        
        if not resume_tests:
            return JSONResponse(content={
                "success": True,
                "data": {
                    "total_tests": 0,
                    "average_score": 0,
                    "best_score": 0,
                    "improvement_trend": [],
                    "grade_distribution": {},
                    "category_performance": {}
                }
            })
        
        # Calculate analytics
        total_tests = len(resume_tests)
        scores = [t.total_score for t in resume_tests if t.total_score is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        
        # Grade distribution
        grade_distribution = {}
        for test in resume_tests:
            grade = test.overall_grade
            if grade:
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # Category performance
        category_performance = {
            "content_quality": [],
            "skills_match": [],
            "experience_achievements": [],
            "format_structure": [],
            "education_certifications": []
        }
        
        for test in resume_tests:
            if test.content_quality_score is not None:
                category_performance["content_quality"].append(test.content_quality_score)
            if test.skills_match_score is not None:
                category_performance["skills_match"].append(test.skills_match_score)
            if test.experience_achievements_score is not None:
                category_performance["experience_achievements"].append(test.experience_achievements_score)
            if test.format_structure_score is not None:
                category_performance["format_structure"].append(test.format_structure_score)
            if test.education_certifications_score is not None:
                category_performance["education_certifications"].append(test.education_certifications_score)
        
        # Calculate averages for each category
        for category, scores_list in category_performance.items():
            if scores_list:
                category_performance[category] = round(sum(scores_list) / len(scores_list), 2)
            else:
                category_performance[category] = 0
        
        # Improvement trend (last 5 tests)
        recent_tests = sorted(resume_tests, key=lambda x: x.analysis_timestamp, reverse=True)[:5]
        improvement_trend = [t.total_score for t in recent_tests if t.total_score is not None]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "total_tests": total_tests,
                "average_score": round(average_score, 2),
                "best_score": best_score,
                "improvement_trend": improvement_trend,
                "grade_distribution": grade_distribution,
                "category_performance": category_performance
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching resume test analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== COMBINED ANALYTICS ==========

@router.get("/combined-analytics/{user_id}")
async def get_combined_test_analytics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get combined analytics for both mock interviews and resume tests"""
    try:
        # Check access permissions
        if current_user.id != user_id and not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get mock interview analytics
        mock_interviews = db.query(MockInterviewSession).filter(
            MockInterviewSession.user_id == user_id
        ).all()
        
        # Get resume test analytics
        resume_tests = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == user_id
        ).all()
        
        # Calculate combined metrics
        total_mock_sessions = len(mock_interviews)
        total_resume_tests = len(resume_tests)
        
        mock_scores = [i.score_overall for i in mock_interviews if i.score_overall is not None]
        resume_scores = [t.total_score for t in resume_tests if t.total_score is not None]
        
        avg_mock_score = sum(mock_scores) / len(mock_scores) if mock_scores else 0
        avg_resume_score = sum(resume_scores) / len(resume_scores) if resume_scores else 0
        
        # Overall performance grade
        all_scores = mock_scores + resume_scores
        overall_grade = "N/A"
        if all_scores:
            avg_overall = sum(all_scores) / len(all_scores)
            if avg_overall >= 90: overall_grade = 'A+'
            elif avg_overall >= 80: overall_grade = 'A'
            elif avg_overall >= 70: overall_grade = 'B+'
            elif avg_overall >= 60: overall_grade = 'B'
            elif avg_overall >= 50: overall_grade = 'C+'
            elif avg_overall >= 40: overall_grade = 'C'
            elif avg_overall >= 30: overall_grade = 'D'
            else: overall_grade = 'F'
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "total_mock_sessions": total_mock_sessions,
                "total_resume_tests": total_resume_tests,
                "average_mock_score": round(avg_mock_score, 2),
                "average_resume_score": round(avg_resume_score, 2),
                "overall_performance_grade": overall_grade,
                "total_activities": total_mock_sessions + total_resume_tests,
                "last_activity": {
                    "mock_interview": mock_interviews[0].started_at.isoformat() if mock_interviews else None,
                    "resume_test": resume_tests[0].analysis_timestamp.isoformat() if resume_tests else None
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching combined analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== HR ACCESS ROUTES ==========

@router.get("/hr/all-mock-interviews")
async def get_all_mock_interviews_hr(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all mock interview results (HR access only)"""
    try:
        if not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="HR access required")
        
        offset = (page - 1) * limit
        
        interviews = db.query(MockInterviewSession).order_by(
            desc(MockInterviewSession.started_at)
        ).offset(offset).limit(limit).all()
        
        total_count = db.query(MockInterviewSession).count()
        
        return JSONResponse(content={
            "success": True,
            "data": [interview.to_dict() for interview in interviews],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching all mock interviews: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/hr/all-resume-tests")
async def get_all_resume_tests_hr(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all resume test results (HR access only)"""
    try:
        if not current_user.is_hr_user():
            raise HTTPException(status_code=403, detail="HR access required")
        
        offset = (page - 1) * limit
        
        resume_tests = db.query(ResumeTestResult).order_by(
            desc(ResumeTestResult.analysis_timestamp)
        ).offset(offset).limit(limit).all()
        
        total_count = db.query(ResumeTestResult).count()
        
        return JSONResponse(content={
            "success": True,
            "data": [test.to_dict() for test in resume_tests],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching all resume tests: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
