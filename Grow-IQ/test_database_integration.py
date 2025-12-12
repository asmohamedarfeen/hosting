#!/usr/bin/env python3
"""
Test script for database integration of test results
This script tests the new models and routes for storing mock interview and resume test results
"""

import os
import sys
import logging
from datetime import datetime
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_sync
from models import User, MockInterviewSession, ResumeTestResult
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_resume_test_result_creation():
    """Test creating a resume test result"""
    try:
        db = get_db_sync()
        
        # Create a sample resume test result
        resume_result = ResumeTestResult(
            user_id=1,  # Assuming user ID 1 exists
            filename="test_resume.pdf",
            filepath="/path/to/test_resume.pdf",
            job_title="Software Engineer",
            company="Tech Corp",
            content_quality_score=22,
            content_quality_explanation="Good professional writing style",
            skills_match_score=20,
            skills_match_explanation="Relevant technical skills included",
            experience_achievements_score=18,
            experience_achievements_explanation="Some achievements could be quantified",
            format_structure_score=12,
            format_structure_explanation="Clean layout and formatting",
            education_certifications_score=8,
            education_certifications_explanation="Good educational background",
            total_score=80,
            overall_grade="B+",
            analysis_timestamp=datetime.now(),
            api_version="1.0",
            model_used="gemini-2.0-flash-exp",
            analysis_duration_ms=2500,
            file_size=1024000,
            file_type="PDF"
        )
        
        # Set strengths, improvements, and recommendations
        resume_result.set_strengths(["Strong technical skills", "Good formatting"])
        resume_result.set_areas_for_improvement(["Quantify achievements", "Add more keywords"])
        resume_result.set_recommendations(["Include specific metrics", "Add industry keywords"])
        
        # Save to database
        db.add(resume_result)
        db.commit()
        db.refresh(resume_result)
        
        logger.info(f"Successfully created resume test result with ID: {resume_result.id}")
        
        # Test retrieval
        retrieved_result = db.query(ResumeTestResult).filter(
            ResumeTestResult.id == resume_result.id
        ).first()
        
        if retrieved_result:
            logger.info(f"Successfully retrieved resume test result: {retrieved_result.filename}")
            logger.info(f"Strengths: {retrieved_result.get_strengths()}")
            logger.info(f"Improvements: {retrieved_result.get_areas_for_improvement()}")
            logger.info(f"Recommendations: {retrieved_result.get_recommendations()}")
        else:
            logger.error("Failed to retrieve resume test result")
        
        # Clean up
        db.delete(resume_result)
        db.commit()
        logger.info("Test resume result cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing resume test result creation: {e}")
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()

def test_mock_interview_session_creation():
    """Test creating a mock interview session with enhanced scoring"""
    try:
        db = get_db_sync()
        
        # Create a sample mock interview session
        interview_session = MockInterviewSession(
            session_uuid="test-session-123",
            user_id=1,  # Assuming user ID 1 exists
            job_role="Software Engineer",
            job_desc="Full-stack development role",
            total_questions=10,
            started_at=datetime.now(),
            ended_at=datetime.now(),
            score_accuracy=22,
            score_clarity=20,
            score_relevance=18,
            score_confidence=19,
            score_overall=79,
            feedback_summary="Good overall performance with room for improvement",
            detailed_feedback=json.dumps({
                "accuracy": "Good technical knowledge",
                "clarity": "Clear communication",
                "relevance": "Relevant answers",
                "confidence": "Moderate confidence level"
            }),
            interview_duration_minutes=25,
            questions_answered=10,
            confidence_level="Medium"
        )
        
        # Set suggestions and transcript
        interview_session.set_suggestions([
            "Practice more technical questions",
            "Improve confidence in responses",
            "Provide more specific examples"
        ])
        interview_session.set_transcript([
            {"turn": 1, "question": "Tell me about yourself", "answer": "I am a software engineer..."},
            {"turn": 2, "question": "What is your experience with Python?", "answer": "I have 3 years..."}
        ])
        
        # Calculate and assign grades
        interview_session.calculate_overall_score()
        interview_session.assign_grades()
        
        # Save to database
        db.add(interview_session)
        db.commit()
        db.refresh(interview_session)
        
        logger.info(f"Successfully created mock interview session with ID: {interview_session.id}")
        logger.info(f"Overall grade: {interview_session.overall_grade}")
        logger.info(f"Accuracy grade: {interview_session.accuracy_grade}")
        logger.info(f"Clarity grade: {interview_session.clarity_grade}")
        logger.info(f"Relevance grade: {interview_session.relevance_grade}")
        logger.info(f"Confidence grade: {interview_session.confidence_grade}")
        
        # Test retrieval
        retrieved_session = db.query(MockInterviewSession).filter(
            MockInterviewSession.id == interview_session.id
        ).first()
        
        if retrieved_session:
            logger.info(f"Successfully retrieved mock interview session: {retrieved_session.job_role}")
            logger.info(f"Suggestions: {retrieved_session.get_suggestions()}")
            logger.info(f"Transcript: {retrieved_session.get_transcript()}")
            logger.info(f"Detailed feedback: {retrieved_session.get_detailed_feedback()}")
        else:
            logger.error("Failed to retrieve mock interview session")
        
        # Clean up
        db.delete(interview_session)
        db.commit()
        logger.info("Test interview session cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing mock interview session creation: {e}")
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()

def test_database_queries():
    """Test various database queries for test results"""
    try:
        db = get_db_sync()
        
        # Test counting records
        resume_count = db.query(ResumeTestResult).count()
        interview_count = db.query(MockInterviewSession).count()
        
        logger.info(f"Current resume test results: {resume_count}")
        logger.info(f"Current mock interview sessions: {interview_count}")
        
        # Test user-specific queries
        user_resume_tests = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == 1
        ).all()
        
        user_interviews = db.query(MockInterviewSession).filter(
            MockInterviewSession.user_id == 1
        ).all()
        
        logger.info(f"User 1 resume tests: {len(user_resume_tests)}")
        logger.info(f"User 1 interviews: {len(user_interviews)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing database queries: {e}")
        return False
    finally:
        if db:
            db.close()

def main():
    """Main test function"""
    logger.info("Starting database integration tests...")
    
    try:
        # Test resume test result creation
        if test_resume_test_result_creation():
            logger.info("✓ Resume test result creation test passed")
        else:
            logger.error("✗ Resume test result creation test failed")
            return False
        
        # Test mock interview session creation
        if test_mock_interview_session_creation():
            logger.info("✓ Mock interview session creation test passed")
        else:
            logger.error("✗ Mock interview session creation test failed")
            return False
        
        # Test database queries
        if test_database_queries():
            logger.info("✓ Database queries test passed")
        else:
            logger.error("✗ Database queries test failed")
            return False
        
        logger.info("All database integration tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
