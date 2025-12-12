#!/usr/bin/env python3
"""
Database migration script for test results tables
This script adds new tables for storing mock interview and resume test results
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DATABASE_URL, engine
from models import Base, MockInterviewSession, ResumeTestResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"Error checking if table {table_name} exists: {e}")
        return False

def migrate_mock_interview_table():
    """Migrate the existing mock_interview_sessions table to add new columns"""
    try:
        with engine.connect() as conn:
            # Check if new columns already exist
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('mock_interview_sessions')]
            
            # Add new columns if they don't exist
            if 'score_confidence' not in columns:
                logger.info("Adding score_confidence column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN score_confidence INTEGER"))
            
            if 'overall_grade' not in columns:
                logger.info("Adding overall_grade column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN overall_grade VARCHAR(10)"))
            
            if 'accuracy_grade' not in columns:
                logger.info("Adding accuracy_grade column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN accuracy_grade VARCHAR(10)"))
            
            if 'clarity_grade' not in columns:
                logger.info("Adding clarity_grade column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN clarity_grade VARCHAR(10)"))
            
            if 'relevance_grade' not in columns:
                logger.info("Adding relevance_grade column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN relevance_grade VARCHAR(10)"))
            
            if 'confidence_grade' not in columns:
                logger.info("Adding confidence_grade column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN confidence_grade VARCHAR(10)"))
            
            if 'detailed_feedback' not in columns:
                logger.info("Adding detailed_feedback column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN detailed_feedback TEXT"))
            
            if 'interview_duration_minutes' not in columns:
                logger.info("Adding interview_duration_minutes column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN interview_duration_minutes INTEGER"))
            
            if 'questions_answered' not in columns:
                logger.info("Adding questions_answered column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN questions_answered INTEGER DEFAULT 0"))
            
            if 'confidence_level' not in columns:
                logger.info("Adding confidence_level column to mock_interview_sessions")
                conn.execute(text("ALTER TABLE mock_interview_sessions ADD COLUMN confidence_level VARCHAR(20)"))
            
            conn.commit()
            logger.info("Successfully migrated mock_interview_sessions table")
            
    except Exception as e:
        logger.error(f"Error migrating mock_interview_sessions table: {e}")
        raise

def create_resume_test_results_table():
    """Create the new resume_test_results table"""
    try:
        if not check_table_exists(engine, 'resume_test_results'):
            logger.info("Creating resume_test_results table")
            ResumeTestResult.__table__.create(engine, checkfirst=True)
            logger.info("Successfully created resume_test_results table")
        else:
            logger.info("resume_test_results table already exists")
            
    except Exception as e:
        logger.error(f"Error creating resume_test_results table: {e}")
        raise

def update_existing_mock_interviews():
    """Update existing mock interview records with calculated grades and scores"""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get all mock interview sessions that don't have grades
        sessions = db.query(MockInterviewSession).filter(
            MockInterviewSession.overall_grade.is_(None)
        ).all()
        
        updated_count = 0
        for session in sessions:
            try:
                # Calculate overall score if not set
                if session.score_overall is None:
                    scores = [session.score_accuracy, session.score_clarity, session.score_relevance]
                    valid_scores = [s for s in scores if s is not None]
                    if valid_scores:
                        session.score_overall = sum(valid_scores)
                
                # Add confidence score if missing (default to average of other scores)
                if session.score_confidence is None:
                    scores = [session.score_accuracy, session.score_clarity, session.score_relevance]
                    valid_scores = [s for s in scores if s is not None]
                    if valid_scores:
                        session.score_confidence = sum(valid_scores) // len(valid_scores)
                
                # Calculate and assign grades
                session.calculate_overall_score()
                session.assign_grades()
                
                # Determine confidence level
                if session.score_accuracy and session.score_clarity and session.score_relevance and session.score_confidence:
                    avg_score = (session.score_accuracy + session.score_clarity + session.score_relevance + session.score_confidence) / 4
                    if avg_score >= 20:
                        session.confidence_level = "High"
                    elif avg_score >= 15:
                        session.confidence_level = "Medium"
                    else:
                        session.confidence_level = "Low"
                
                updated_count += 1
                
            except Exception as e:
                logger.warning(f"Error updating session {session.id}: {e}")
                continue
        
        db.commit()
        logger.info(f"Updated {updated_count} existing mock interview sessions")
        
    except Exception as e:
        logger.error(f"Error updating existing mock interviews: {e}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()

def main():
    """Main migration function"""
    try:
        logger.info("Starting test results database migration...")
        
        # Migrate existing mock interview table
        migrate_mock_interview_table()
        
        # Create new resume test results table
        create_resume_test_results_table()
        
        # Update existing mock interview records
        update_existing_mock_interviews()
        
        logger.info("Test results database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
