# Qrow IQ - FastAPI Version

A professional networking platform built with FastAPI, SQLAlchemy, and modern web technologies.

## Features

- User authentication and profiles
- Professional networking and connections
- Job postings and applications
- Real-time notifications
- Analytics dashboard
- File uploads (images)
- Responsive web interface

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy with SQLite (configurable for PostgreSQL)
- **Authentication**: Passlib with bcrypt
- **Templates**: Jinja2
- **Static Files**: FastAPI StaticFiles
- **Server**: Uvicorn

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Qrow IQ
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

## Environment Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- `UPLOAD_FOLDER`: Path for file uploads (default: static/uploads)

## API Endpoints

- `GET /`: Main dashboard
- `GET /profile`: User profile page
- `GET /jobs`: Job listings
- `GET /connections`: User connections
- `GET /notifications`: User notifications
- `GET /analytics`: Analytics dashboard
- `GET /messages`: Messages page
- `POST /create_post`: Create a new post
- `POST /update_profile`: Update user profile
- `POST /like_post/{post_id}`: Like a post
- `GET /create_user`: User registration form
- `POST /create_user`: Create new user account
- `GET /init_sample_data`: Initialize sample data

## Database

The application uses SQLAlchemy with automatic table creation. The database file will be created automatically as `dashboard.db` in the instance directory.

## File Structure

```
Qrow IQ/
├── app.py              # FastAPI application setup
├── main.py             # Application entry point
├── routes.py           # API routes and endpoints
├── models.py           # Database models
├── templates/          # Jinja2 HTML templates
├── static/             # Static files (CSS, JS, uploads)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Development

- The application runs on port 8000 by default
- Hot reload is enabled for development
- Static files are served from the `/static` directory
- File uploads are stored in `static/uploads/`

## Migration from Flask

This application was migrated from Flask to FastAPI. Key changes include:

- Replaced Flask with FastAPI
- Converted Flask routes to FastAPI endpoints
- Updated database models to use pure SQLAlchemy
- Replaced Flask-SQLAlchemy with direct SQLAlchemy
- Updated templates to remove Flask-specific functions
- Added proper async/await support
- Improved type hints and validation
