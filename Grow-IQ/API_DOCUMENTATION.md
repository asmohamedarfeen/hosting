# Qrow IQ Social API Documentation

## Overview
Qrow IQ is a professional networking platform with LinkedIn-like features including friend connections, domain-based user permissions, events, and job postings.

## User Types & Permissions

### Normal Users (Free Email)
- ✅ Can post content
- ✅ Can send/receive friend requests
- ✅ Can view jobs and events
- ✅ Can register for events
- ❌ Cannot post jobs
- ❌ Cannot host events

### Domain Users (Company Email)
- ✅ All normal user permissions
- ✅ Can post job listings
- ✅ Can host events
- ✅ Can post company announcements
- ✅ Verified company status

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Core Routes
- `GET /` - Main dashboard
- `GET /profile` - User profile
- `GET /jobs` - Job listings
- `GET /connections` - Professional connections
- `GET /notifications` - User notifications

### Social Routes (Prefix: `/social`)

#### Friend Requests
```
POST /social/friend-request/send
- receiver_id: int (required)
- message: str (optional)

POST /social/friend-request/{request_id}/respond
- response: str (required) - "accept" or "decline"

GET /social/friend-requests
- Returns pending friend requests for current user
```

#### Events (Domain Users Only)
```
POST /social/events/create
- title: str (required)
- description: str (required)
- event_type: str (required) - "webinar", "conference", "meetup", "workshop"
- start_date: str (required) - ISO format
- end_date: str (required) - ISO format
- location: str (required)
- is_virtual: bool (optional)
- meeting_link: str (optional)
- max_participants: int (optional)
- registration_required: bool (optional)

GET /social/events
- event_type: str (optional) - Filter by event type
- is_virtual: bool (optional) - Filter virtual/in-person events

POST /social/events/{event_id}/register
- Register current user for an event
```

#### Enhanced Posts
```
POST /social/posts/create
- content: str (required)
- post_type: str (optional) - "general", "job", "event", "announcement"
- image: file (optional)
- is_public: bool (optional) - Default true
```

#### Job Postings (Domain Users Only)
```
POST /social/jobs/create
- title: str (required)
- company: str (required)
- location: str (required)
- job_type: str (required) - "full-time", "part-time", "contract", "internship"
- salary_range: str (required)
- description: str (required)
- requirements: str (required)
- benefits: str (optional)
- application_deadline: str (optional) - ISO format
```

#### User Management
```
POST /social/users/verify-domain
- email: str (required) - Company email to verify
- company_name: str (required)
- verification_code: str (required)

GET /social/users/profile/{user_id}
- Returns detailed user profile with posts and connection count
```

#### Search & Discovery
```
GET /social/search/users
- query: str (required) - Search terms
- user_type: str (optional) - Filter by user type
- location: str (optional) - Filter by location

GET /social/search/jobs
- query: str (required) - Search terms
- location: str (optional) - Filter by location
- job_type: str (optional) - Filter by job type
```

## Database Schema

### Core Tables
- `users` - User accounts with type and verification status
- `posts` - User posts with type and visibility
- `jobs` - Job listings (domain users only)
- `events` - Events (domain users only)
- `connections` - Professional connections
- `friend_requests` - Friend request system
- `notifications` - User notifications
- `comments` - Post comments
- `messages` - Direct messages
- `conversations` - Message conversations

### Key Features
- **Domain Verification**: Automatic detection of company vs. free email domains
- **Permission System**: Role-based access control for different user types
- **Friend System**: Separate from professional connections
- **Event Management**: Full event lifecycle with registration
- **Job Postings**: Company-verified job listings
- **Search**: Advanced search across users, jobs, and content

## Usage Examples

### 1. Send Friend Request
```bash
curl -X POST "http://localhost:8000/social/friend-request/send" \
  -F "receiver_id=2" \
  -F "message=Hi! I'd like to connect with you."
```

### 2. Create Event (Domain User)
```bash
curl -X POST "http://localhost:8000/social/events/create" \
  -F "title=Tech Meetup 2024" \
  -F "description=Join us for networking and tech talks" \
  -F "event_type=meetup" \
  -F "start_date=2024-02-15T18:00:00" \
  -F "end_date=2024-02-15T21:00:00" \
  -F "location=San Francisco, CA" \
  -F "is_virtual=false"
```

### 3. Post Job (Domain User)
```bash
curl -X POST "http://localhost:8000/social/jobs/create" \
  -F "title=Senior Software Engineer" \
  -F "company=TechCorp Inc." \
  -F "location=Remote" \
  -F "job_type=full-time" \
  -F "salary_range=$120k - $160k" \
  -F "description=We're looking for an experienced engineer..." \
  -F "requirements=5+ years experience, Python, React"
```

### 4. Search Users
```bash
curl "http://localhost:8000/social/search/users?query=software engineer&location=San Francisco"
```

### 5. Verify Domain Email
```bash
curl -X POST "http://localhost:8000/social/users/verify-domain" \
  -F "email=john@company.com" \
  -F "company_name=Company Inc." \
  -F "verification_code=123456"
```

## Authentication & Security

- All endpoints require user authentication
- Domain verification ensures company email authenticity
- Permission checks prevent unauthorized access
- Input validation and sanitization
- Error handling with detailed messages

## Development Notes

- Built with FastAPI for high performance
- SQLAlchemy ORM for database operations
- Jinja2 templates for HTML responses
- File upload support for images
- Real-time notifications system
- Scalable architecture for future enhancements

## Future Enhancements

- Real-time messaging with WebSockets
- Advanced analytics and insights
- Company pages and branding
- Integration with external job boards
- Mobile app API endpoints
- Advanced search filters
- Recommendation engine
