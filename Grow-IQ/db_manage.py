#!/usr/bin/env python3
"""
Database Management Script for Qrow IQ
Handles database initialization, migrations, and maintenance
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and return the result"""
    import subprocess
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None

def init_database():
    """Initialize the database with Alembic"""
    logger.info("Initializing database with Alembic...")
    
    # Check if migrations directory exists
    if not os.path.exists("migrations"):
        logger.info("Creating migrations directory...")
        run_command("alembic init migrations")
    
    # Create initial migration
    logger.info("Creating initial migration...")
    result = run_command("alembic revision --autogenerate -m 'Initial migration'")
    if result:
        logger.info("Initial migration created successfully")
    else:
        logger.error("Failed to create initial migration")
        return False
    
    # Run the migration
    logger.info("Running initial migration...")
    result = run_command("alembic upgrade head")
    if result:
        logger.info("Database initialized successfully")
        return True
    else:
        logger.error("Failed to initialize database")
        return False

def run_migrations():
    """Run pending database migrations"""
    logger.info("Running database migrations...")
    result = run_command("alembic upgrade head")
    if result:
        logger.info("Migrations completed successfully")
        return True
    else:
        logger.error("Migrations failed")
        return False

def create_migration(message):
    """Create a new migration with the given message"""
    if not message:
        message = "Database changes"
    
    logger.info(f"Creating migration: {message}")
    result = run_command(f'alembic revision --autogenerate -m "{message}"')
    if result:
        logger.info("Migration created successfully")
        return True
    else:
        logger.error("Failed to create migration")
        return False

def show_migration_history():
    """Show migration history"""
    logger.info("Migration history:")
    result = run_command("alembic history")
    if result:
        print(result)
    else:
        logger.error("Failed to show migration history")

def show_current_revision():
    """Show current database revision"""
    logger.info("Current database revision:")
    result = run_command("alembic current")
    if result:
        print(result)
    else:
        logger.error("Failed to show current revision")

def reset_database():
    """Reset the database (WARNING: This will delete all data)"""
    logger.warning("WARNING: This will delete all data in the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        logger.info("Resetting database...")
        # Remove the database file
        db_file = "dashboard.db"
        if os.path.exists(db_file):
            os.remove(db_file)
            logger.info(f"Removed {db_file}")
        
        # Reinitialize
        if init_database():
            logger.info("Database reset successfully")
        else:
            logger.error("Failed to reset database")
    else:
        logger.info("Database reset cancelled")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("""
Database Management Script for Qrow IQ

Usage:
  python db_manage.py <command> [options]

Commands:
  init          Initialize database with Alembic
  migrate       Run pending migrations
  create <msg>  Create new migration with message
  history       Show migration history
  current       Show current revision
  reset         Reset database (WARNING: deletes all data)
  help          Show this help message

Examples:
  python db_manage.py init
  python db_manage.py migrate
  python db_manage.py create "Add user profile fields"
  python db_manage.py history
  python db_manage.py current
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        init_database()
    elif command == "migrate":
        run_migrations()
    elif command == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else "Database changes"
        create_migration(message)
    elif command == "history":
        show_migration_history()
    elif command == "current":
        show_current_revision()
    elif command == "reset":
        reset_database()
    elif command == "help":
        main()  # Show help
    else:
        logger.error(f"Unknown command: {command}")
        main()  # Show help

if __name__ == "__main__":
    main()
