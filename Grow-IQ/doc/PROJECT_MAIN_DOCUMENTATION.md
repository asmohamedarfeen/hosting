# Grow-IQ 2025 - Complete Project Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Core Features](#core-features)
5. [Professional Networking](#professional-networking)
6. [Job Management System](#job-management-system)
7. [HR Dashboard](#hr-dashboard)
8. [AI-Powered Features](#ai-powered-features)
9. [Communication Features](#communication-features)
10. [Activity Tracking](#activity-tracking)
11. [Security & Performance](#security--performance)
12. [Deployment & Configuration](#deployment--configuration)
13. [API Documentation](#api-documentation)
14. [Development Guide](#development-guide)

---

## 🎯 Project Overview

**Grow-IQ 2025** (formerly Qrow IQ / CareerConnect) is a comprehensive professional networking and career development platform. It combines LinkedIn-style networking with advanced job management, AI-powered career tools, and real-time communication features to create a complete career ecosystem.

### Key Highlights
- **Professional Networking**: Build and manage your professional network
- **Job Management**: Post jobs, apply, and track applications
- **HR Tools**: Complete hiring management system
- **AI Integration**: Resume testing and mock interviews powered by AI
- **Real-time Communication**: Messaging and connection management
- **Activity Tracking**: Streak calendar for habit building
- **Enterprise Ready**: Production-grade security, logging, and monitoring

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Session-based with bcrypt password hashing
- **API**: RESTful API with WebSocket support
- **File Storage**: Local storage / Azure Blob Storage (configurable)

### Frontend
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS, Custom CSS
- **Icons**: Font Awesome
- **State Management**: React Hooks
- **HTTP Client**: Fetch API

### AI & External Services
- **AI Provider**: Google Gemini AI
- **Speech Recognition**: Web Speech API + Python service
- **Text-to-Speech**: Browser Web Speech API

### Infrastructure
- **Server**: Uvicorn
- **Containerization**: Docker & Docker Compose
- **Deployment**: Azure App Service (configurable)
- **Monitoring**: Custom logging system

---

## 🏗️ System Architecture

### Application Structure
```
Grow-IQ-2025/
├── app.py                      # Main FastAPI application
├── models.py                   # Database models
├── database.py                 # Database configuration
├── config.py                   # Configuration management
├── security.py                 # Security utilities
├── logging_config.py          # Logging configuration
│
├── Routes/
│   ├── auth_routes.py         # Authentication endpoints
│   ├── home_routes.py         # Home page routes
│   ├── job_routes.py          # Job management routes
│   ├── hr_routes.py           # HR dashboard routes
│   ├── connection_routes.py   # Connection management routes
│   ├── message_routes.py      # Messaging routes
│   ├── workshop_routes.py     # Workshop management
│   ├── streak_routes.py       # Activity tracking routes
│   ├── resume_tester_routes.py # Resume testing routes
│   └── mockinterview_routes.py # Mock interview routes
│
├── Modules/
│   ├── resume_tester/         # Resume testing module
│   ├── mockinterviwe/         # Mock interview module
│   └── message/               # Messaging module
│
├── fronted/
│   └── client/
│       └── src/
│           ├── pages/          # React pages
│           ├── components/    # React components
│           └── services/      # API services
│
└── static/                    # Static assets
    ├── css/                   # Stylesheets
    ├── js/                    # JavaScript files
    └── uploads/               # User uploads
```

### Database Schema
- **Users**: User profiles and authentication
- **Posts**: Social media posts and content
- **Jobs**: Job postings and listings
- **JobApplications**: Job application tracking
- **Connections**: Professional connections
- **FriendRequests**: Connection request management
- **Messages**: Real-time messaging
- **Streaks**: Activity streak tracking
- **StreakLogs**: Daily activity logs
- **Workshops**: Workshop management
- **Sessions**: User session management

---

## ✨ Core Features

### 1. User Authentication & Management

#### Registration & Login
- **Email-based registration** with validation
- **Secure password hashing** using bcrypt
- **Session-based authentication** with secure cookies
- **Email verification** system
- **Password reset** functionality
- **Google OAuth** integration (optional)

#### User Profiles
- **Complete profile management**: Name, title, company, location, bio
- **Profile picture upload** with validation
- **Skills and experience** tracking
- **Professional summary** and portfolio links
- **User type classification**: Normal, Domain (HR), Premium

#### User Types
- **Normal Users**: Standard networking and job application features
- **Domain Users (HR)**: Access to HR dashboard and job posting
- **Premium Users**: Advanced features and analytics

### 2. Landing Page & Navigation

#### Landing Page Features
- **Hero section** with call-to-action
- **Feature highlights** and statistics
- **Responsive design** for all devices
- **Modern UI** with gradient backgrounds
- **Smooth animations** and transitions

#### Navigation System
- **Left sidebar navigation** with icons
- **Quick action buttons** for key features
- **Breadcrumb navigation** for deep pages
- **Mobile-responsive** hamburger menu
- **Active route highlighting**

### 3. Home Dashboard

#### Dashboard Components
- **Activity feed** with posts and updates
- **Quick actions** sidebar
- **Recent connections** widget
- **Job recommendations** section
- **Statistics cards** (connections, posts, etc.)
- **Notification center**

---

## 🔗 Professional Networking

### Connection Management

#### Core Features
- **Send Connection Requests**: Send personalized requests to professionals
- **Accept/Decline Requests**: Manage incoming connection requests
- **Withdraw Requests**: Cancel sent requests before response
- **Remove Connections**: Remove existing connections
- **Connection History**: Track all connection activities

#### Intelligent Suggestions
- **Mutual Connections**: Prioritize users with shared connections
- **Company Matching**: Suggest colleagues from same organization
- **Location-Based**: Connect with professionals in your area
- **Industry Alignment**: Find people in your field
- **Skill Compatibility**: Match based on professional skills

#### Network Analytics
- **Connection Statistics**: Total connections, pending requests
- **Network Growth**: Track connection growth over time
- **Industry Distribution**: See network's industry spread
- **Mutual Connection Counts**: Identify most connected contacts

#### Advanced Search & Filtering
- **Multi-criteria Search**: Search by name, company, title, skills
- **Location Filtering**: Find connections in specific areas
- **Company Filtering**: Filter by organization
- **Sorting Options**: Sort by name, company, activity, mutual connections

### Social Features

#### Posts & Content Sharing
- **Create Posts**: Share text and image posts
- **Like & Comment**: Engage with network content
- **Post Feed**: View posts from connections
- **Image Upload**: Share professional photos
- **Post Analytics**: Track engagement metrics

---

## 💼 Job Management System

### For Job Seekers

#### Job Discovery
- **Job Listings**: Browse all available positions
- **Advanced Search**: Filter by location, company, keywords
- **Job Recommendations**: AI-powered job suggestions
- **Saved Jobs**: Bookmark favorite positions
- **Job Alerts**: Get notified about new matches

#### Application Process
- **Easy Application**: Streamlined application forms
- **Resume Upload**: Upload resume for applications
- **Cover Letter**: Optional cover letter submission
- **Application Tracking**: Track application status
- **Application History**: View all past applications

### For HR Professionals

#### Job Posting
- **Create Job Postings**: Post new positions
- **Job Management**: Edit and manage posted jobs
- **Application Review**: Review incoming applications
- **Candidate Evaluation**: Rate and evaluate candidates
- **Status Management**: Track application workflow

#### Job Analytics
- **Application Metrics**: Track application counts
- **Performance Analytics**: Monitor job performance
- **Candidate Insights**: Analyze applicant demographics
- **Time-to-Hire**: Track hiring efficiency

### Job Features
- **Job Categories**: Organize by industry and type
- **Salary Information**: Display salary ranges
- **Remote Options**: Indicate remote work availability
- **Company Profiles**: Link to company information
- **Application Deadlines**: Set and track deadlines

---

## 👔 HR Dashboard

### Access Control
- **HR-Only Access**: Automatic detection based on company email domains
- **Role-Based Permissions**: Secure authentication with role checks
- **Development Mode**: Testing mode for any user type

### Dashboard Overview
- **Real-time Statistics**: Application counts and metrics
- **Recent Applications**: Latest application notifications
- **Quick Actions**: Common task shortcuts
- **Interactive Charts**: Application trend visualization

### Application Management
- **Comprehensive Tracking**: Complete application lifecycle
- **Status Management**: 
  - Pending → Reviewed → Interview → Rejected/Hired
- **Bulk Actions**: Process multiple applications
- **Filtering & Search**: Find specific applications
- **Notes & Ratings**: Add HR notes and candidate ratings

### Candidate Profiles
- **Detailed Information**: Skills, experience, education
- **Application History**: View all applications from candidate
- **Contact Information**: Email and profile links
- **Advanced Search**: Filter candidates by skills, experience, location

### Job Management
- **View All Jobs**: See all posted positions
- **Job Performance**: Application counts and metrics
- **Quick Access**: Direct links to job applications
- **Job Editing**: Update job details

### Analytics & Reporting
- **Status Breakdown**: Application status distribution
- **Hiring Funnel**: Visualize hiring process
- **Time-to-Hire**: Track hiring efficiency
- **Performance Insights**: Data-driven hiring decisions

---

## 🤖 AI-Powered Features

### Resume Tester

#### Features
- **AI-Powered Analysis**: Google Gemini AI integration
- **ATS Scoring**: Comprehensive ATS (Applicant Tracking System) analysis
- **5-Category Scoring**:
  - Content Quality (25 points)
  - Skills Match (25 points)
  - Experience & Achievements (25 points)
  - Format & Structure (15 points)
  - Education & Certifications (10 points)

#### Functionality
- **PDF Upload**: Upload resume for analysis
- **Detailed Reports**: Comprehensive scoring with explanations
- **Performance Grading**: A+ to D grading system
- **Strengths & Recommendations**: Improvement suggestions
- **Score Management**: Download and manage score reports
- **User-Specific Tracking**: Personal score history

### Mock Interview

#### Features
- **AI-Powered Interviews**: Google Gemini AI for intelligent questioning
- **Professional HR-Style**: Mimics real HR interview experience
- **Progressive Difficulty**: Easy → Medium → Hard questions
- **Balanced Questions**: Technical and behavioral questions
- **Context-Aware**: Follows conversation flow naturally

#### Interview Flow
1. **Role Selection**: Enter job role and description
2. **Preparation**: Review instructions and setup
3. **Live Interview**: Real-time AI conversation
4. **Voice Integration**: Speech recognition and synthesis
5. **Session Management**: Persistent conversation history

#### Technical Features
- **Speech Recognition**: Browser-based voice input
- **Text-to-Speech**: AI responses with voice
- **Real-time Communication**: WebSocket-style messaging
- **Session Tracking**: User-specific interview sessions

---

## 💬 Communication Features

### Messaging System

#### Real-time Messaging
- **WebSocket Support**: Real-time chat via WebSocket connections
- **Message Persistence**: All messages stored in database
- **Chat History**: Retrieve full conversation history
- **Read Receipts**: Mark messages as read
- **Typing Indicators**: Real-time typing notifications

#### Messaging Features
- **One-on-One Chat**: Direct messaging between connections
- **Message Search**: Find specific messages
- **Message Status**: Sent, delivered, read indicators
- **File Sharing**: Share files and documents
- **Connection Requirement**: Only message mutually connected users

### Connection Communication
- **Personal Messages**: Add notes to connection requests
- **Profile Viewing**: View detailed professional profiles
- **Mutual Connection Discovery**: See shared connections
- **Activity Feed**: View recent posts and updates

---

## 📅 Activity Tracking

### Streaks Calendar

#### Calendar Features
- **Monthly View**: Navigate through months
- **Visual Indicators**: Green days for completed activities
- **Streak Indicators**: Yellow dots for current streaks
- **Today Highlighting**: Current day highlighted
- **Responsive Design**: Works on all devices

#### Activity Types
- Coding
- Networking
- Learning
- Exercise
- Reading
- Writing
- Meditation
- Planning

#### Statistics Dashboard
- **Total Current Streak**: Sum of all current streaks
- **Longest Streak Ever**: Highest streak achieved
- **Activity Types**: Number of tracked activities
- **Today's Activities**: Count of today's logged activities

#### Activity Logging
- **Multiple Activity Types**: Track various activities
- **Optional Descriptions**: Add details about activities
- **Real-time Updates**: Calendar updates immediately
- **Duplicate Prevention**: Can't log same activity twice per day

#### Streak Management
- **Automatic Calculation**: Streaks calculated automatically
- **Streak Reset**: Missing a day resets counter
- **Longest Streak Tracking**: Records highest streak
- **Visual Progress**: See progress in calendar

---

## 🔒 Security & Performance

### Security Features

#### Authentication & Authorization
- **Secure Password Hashing**: bcrypt with salt
- **Session Management**: Secure session tokens
- **Role-Based Access Control**: User type permissions
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Protection**: Cross-site scripting prevention

#### Input Validation
- **Email Validation**: RFC-compliant email checking
- **SQL Injection Protection**: ORM-based queries
- **HTML Sanitization**: Dangerous tag removal
- **File Upload Security**: Extension and size validation
- **Rate Limiting**: Prevent abuse and ensure fair usage

#### Security Headers
- **X-Frame-Options**: DENY
- **X-Content-Type-Options**: nosniff
- **X-XSS-Protection**: 1; mode=block
- **Content-Security-Policy**: Comprehensive CSP rules

### Performance Optimizations

#### Database
- **Connection Pooling**: Configurable pool sizes
- **Query Optimization**: Efficient database queries
- **Indexing**: Proper database indexes
- **Health Monitoring**: Real-time status checks

#### Application
- **Async Support**: FastAPI async capabilities
- **Static File Serving**: Optimized file delivery
- **Caching**: Redis integration ready
- **Load Balancing**: Multiple worker support

#### Frontend
- **Lazy Loading**: Load components on demand
- **Debounced Search**: Reduce API calls
- **Efficient DOM Manipulation**: Minimal reflows
- **CSS Animations**: Transform-based animations

### Monitoring & Logging

#### Logging System
- **Structured Logging**: Timestamps and context
- **Color-coded Console**: Easy debugging
- **Rotating File Logs**: Main, errors, security logs
- **Specialized Loggers**: Security and performance logging
- **Log Rotation**: Automatic log management

#### Health Monitoring
- **Application Health**: `/health` endpoint
- **Database Connectivity**: Automatic checks
- **System Uptime**: Monitoring
- **Performance Metrics**: Request timing
- **Environment Information**: Configuration details

---

## 🚀 Deployment & Configuration

### Environment Configuration

#### Required Environment Variables
```env
# Application Settings
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/growiq

# Security Settings
CORS_ORIGINS=https://yourdomain.com
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# File Upload Settings
MAX_FILE_SIZE=16777216
UPLOAD_FOLDER=./static/uploads

# API Settings
API_RATE_LIMIT=100

# AI Services
GOOGLE_AI_API_KEY=your-google-ai-api-key
```

### Deployment Options

#### Option 1: Traditional Server Deployment
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx postgresql

# Setup database
sudo -u postgres psql
CREATE DATABASE growiq;
CREATE USER growiq WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE growiq TO growiq;

# Install application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo systemctl enable growiq
sudo systemctl start growiq
```

#### Option 2: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

#### Option 3: Azure App Service
- **App Service**: Web application hosting
- **PostgreSQL**: Azure Database for PostgreSQL
- **Blob Storage**: File storage for uploads
- **Application Insights**: Monitoring and analytics

### Database Migration
```bash
# Export SQLite data
sqlite3 dashboard.db .dump > backup.sql

# Import to PostgreSQL
psql -U growiq -d growiq < backup.sql
```

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### Get Current User
```http
GET /api/auth/profile
Cookie: session_token=...
```

### Job Endpoints

#### Get Jobs
```http
GET /api/jobs?search=python&location=NYC&limit=20&offset=0
```

#### Apply for Job
```http
POST /api/jobs/apply
Content-Type: multipart/form-data

{
  "job_id": 1,
  "cover_letter": "Dear Hiring Manager...",
  "resume": <file>
}
```

#### Post Job (HR Only)
```http
POST /api/jobs/post
Content-Type: application/json

{
  "title": "Software Engineer",
  "company": "Tech Corp",
  "location": "New York, NY",
  "description": "Job description...",
  "requirements": "Requirements...",
  "salary": "$100,000 - $150,000"
}
```

### Connection Endpoints

#### Send Connection Request
```http
POST /connections/api/request
Content-Type: application/json

{
  "receiver_id": 123
}
```

#### Accept Connection
```http
POST /connections/api/accept/{user_id}
```

#### Get Connections
```http
GET /connections/api/connections
```

### Messaging Endpoints

#### Send Message
```http
POST /api/messages/send
Content-Type: application/json

{
  "receiver_id": 123,
  "content": "Hello!"
}
```

#### Get Chat History
```http
GET /api/messages/chat/{user_id}
```

#### WebSocket Connection
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/messages/ws/${userId}?token=${token}`);
```

### HR Dashboard Endpoints

#### Get Applications
```http
GET /hr/applications?status=pending&job_id=1&limit=20&offset=0
```

#### Update Application Status
```http
PUT /hr/applications/{id}/status
Content-Type: application/json

{
  "status": "interview",
  "notes": "Strong technical background",
  "hr_rating": 4
}
```

#### Search Candidates
```http
GET /hr/candidates?search=python&experience_min=3&location=NYC
```

### Resume Tester Endpoints

#### Score Resume
```http
POST /resume-tester/score-resume
Content-Type: multipart/form-data

{
  "resume": <pdf_file>
}
```

### Mock Interview Endpoints

#### Start Interview
```http
POST /mock-interview/start
Content-Type: application/json

{
  "job_role": "Software Engineer",
  "job_description": "Full-stack developer position..."
}
```

#### Send Message
```http
POST /mock-interview/message
Content-Type: application/json

{
  "session_id": "abc123",
  "message": "I have 5 years of experience..."
}
```

### Streaks Endpoints

#### Log Activity
```http
POST /streaks/log-activity
Content-Type: application/json

{
  "activity_type": "coding",
  "description": "Worked on API endpoints"
}
```

#### Get Streak Stats
```http
GET /streaks/get-streak-stats
```

#### Get Calendar Data
```http
GET /streaks/get-calendar-data?month=11&year=2024
```

---

## 👨‍💻 Development Guide

### Setup Development Environment

#### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL 13+ (optional, SQLite for development)
- Git

#### Installation Steps
```bash
# Clone repository
git clone <repository-url>
cd Grow-IQ-2025-

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd fronted/client
npm install

# Setup database
python -c "from database import init_db; init_db()"

# Run backend
python start.py

# Run frontend (in separate terminal)
cd fronted/client
npm start
```

### Development Workflow

#### Code Structure
- **Backend**: Follow FastAPI best practices
- **Frontend**: React with TypeScript
- **Database**: Use SQLAlchemy ORM
- **API**: RESTful design principles

#### Testing
```bash
# Run backend tests
pytest

# Run frontend tests
cd fronted/client
npm test

# Run with coverage
pytest --cov=.
```

#### Code Quality
- **Linting**: Use flake8 for Python, ESLint for TypeScript
- **Formatting**: Use black for Python, Prettier for TypeScript
- **Type Checking**: Use mypy for Python, TypeScript compiler

### Adding New Features

#### Backend Feature
1. Create route file in root directory (e.g., `new_feature_routes.py`)
2. Define models in `models.py` if needed
3. Add routes to `app.py`
4. Create API endpoints
5. Add tests

#### Frontend Feature
1. Create component in `fronted/client/src/components/`
2. Create page in `fronted/client/src/pages/`
3. Add route in router configuration
4. Create service in `fronted/client/src/services/`
5. Add styling

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 📖 Feature-Specific Documentation

For detailed documentation on specific features, refer to:

- **Connection System**: `CONNECTION_SYSTEM_README.md`
- **Connection Management**: `CONNECTION_MANAGEMENT_README.md`
- **HR Dashboard**: `HR_DASHBOARD_README.md`
- **Jobs Redesign**: `JOBS_REDESIGN_README.md`
- **Resume Tester**: `RESUME_TESTER_INTEGRATION_README.md`
- **Mock Interview**: `MOCK_INTERVIEW_INTEGRATION_README.md`
- **Messaging**: `MESSAGE_README.md`
- **Streaks Calendar**: `STREAKS_CALENDAR_README.md`
- **Speech Recognition**: `SPEECH_RECOGNITION_README.md`
- **Enhanced Features**: `ENHANCED_FEATURES_README.md`

---

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database status
sudo systemctl status postgresql

# Test connection
python -c "from database_enhanced import test_db_connection; print(test_db_connection())"
```

#### Port Already in Use
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Kill process if needed
sudo kill -9 <PID>
```

#### Authentication Issues
- Check session token in cookies
- Verify user is logged in
- Check authentication middleware
- Review session expiration settings

#### File Upload Issues
- Check file size limits
- Verify upload directory permissions
- Check file type validation
- Review storage configuration

### Log Analysis
```bash
# View application logs
tail -f logs/qrowiq.log

# View error logs
tail -f logs/errors.log

# View security logs
tail -f logs/security.log
```

---

## 🎯 Future Enhancements

### Planned Features
- **Advanced Analytics**: Network insights and recommendations
- **Mobile App**: Native mobile applications
- **Video Interviews**: Integrated video call interviews
- **AI Recommendations**: ML-based job and connection suggestions
- **Integration APIs**: Connect with external platforms
- **Advanced Search**: Elasticsearch integration
- **Real-time Notifications**: WebSocket-based notifications
- **Workshop Management**: Enhanced workshop features

### Technical Improvements
- **Microservices**: Break down into smaller services
- **Kubernetes**: Container orchestration for scaling
- **CI/CD**: Automated deployment pipelines
- **Advanced Caching**: Redis integration
- **Background Tasks**: Celery for async processing
- **Performance Monitoring**: APM integration

---

## 📞 Support & Resources

### Getting Help
1. **Documentation**: Review this and feature-specific documentation
2. **API Documentation**: Check `/docs` endpoint for interactive API docs
3. **Logs**: Review application logs for errors
4. **Health Check**: Verify system status via `/health` endpoint

### Contributing
- Follow existing code patterns
- Write tests for new features
- Update documentation
- Submit pull requests

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Built with modern web technologies and best practices
- Inspired by LinkedIn's professional networking features
- Designed for scalability and maintainability
- Focused on user experience and professional networking

---

**Last Updated**: November 2024  
**Version**: 2025.1.0  
**Status**: Production Ready ✅

---

*For questions, issues, or feature requests, please refer to the troubleshooting section or check the application logs.*

