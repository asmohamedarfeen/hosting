# LinkedIn-like Connection + Messaging App

A production-ready FastAPI application that provides LinkedIn-style user connections and real-time messaging capabilities. Built with modern Python practices, JWT authentication, and WebSocket support.

## 🚀 Features

### User System
- **User Registration & Login**: Secure JWT-based authentication
- **Profile Management**: Update name, email, and bio
- **User Discovery**: List all users (excluding current user)

### Connection System (LinkedIn-style)
- **Connection Requests**: Send connection requests to other users
- **Accept/Reject**: Handle incoming connection requests
- **Connection Status**: Track pending, accepted, and rejected connections
- **Mutual Connections**: Only allow messaging between mutually connected users

### Real-time Messaging
- **WebSocket Support**: Real-time chat via WebSocket connections
- **Message Persistence**: Store all messages in database
- **Chat History**: Retrieve conversation history
- **Read Receipts**: Mark messages as read
- **Typing Indicators**: Real-time typing notifications

### Technical Features
- **FastAPI Framework**: Modern, fast web framework
- **SQLAlchemy ORM**: Robust database operations
- **JWT Authentication**: Secure token-based auth
- **Database Migrations**: Alembic for schema management
- **CORS Support**: Cross-origin resource sharing
- **Production Ready**: Error handling, logging, and monitoring

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLite (local dev) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **WebSocket**: FastAPI WebSocket support
- **Migrations**: Alembic
- **Validation**: Pydantic v2

## 📋 Requirements

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd message

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Database configuration
DATABASE_URL=sqlite:///./app.db

# JWT configuration
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: PostgreSQL for production
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 3. Run the Application

```bash
# Run with auto-reload (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/api/info

## 📚 API Endpoints

### Authentication
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile

### Users
- `GET /api/v1/users/` - List all users
- `GET /api/v1/users/{user_id}` - Get specific user

### Connections
- `POST /api/v1/connections/` - Send connection request
- `PUT /api/v1/connections/{id}/accept` - Accept connection
- `PUT /api/v1/connections/{id}/reject` - Reject connection
- `GET /api/v1/connections/` - List connections
- `GET /api/v1/connections/{id}` - Get connection details
- `DELETE /api/v1/connections/{id}` - Delete connection

### Messages
- `POST /api/v1/messages/` - Send message
- `GET /api/v1/messages/chat/{user_id}` - Get chat history
- `PUT /api/v1/messages/{id}/read` - Mark message as read
- `WS /api/v1/messages/ws/{user_id}` - WebSocket connection

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

1. **Register a new user**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john@example.com",
       "password": "securepassword123",
       "bio": "Software Developer"
     }'
```

2. **Login**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com",
       "password": "securepassword123"
     }'
```

## 💬 Real-time Messaging

### WebSocket Connection

Connect to the WebSocket endpoint with your JWT token:

```javascript
const token = "your-jwt-token";
const userId = 123;
const ws = new WebSocket(`ws://localhost:8000/api/v1/messages/ws/${userId}?token=${token}`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send typing indicator
ws.send(JSON.stringify({
    type: "typing",
    receiver_id: 456
}));

// Mark message as read
ws.send(JSON.stringify({
    type: "read",
    message_id: 789
}));
```

## 🗄️ Database

### Local Development (SQLite)
The app uses SQLite by default for local development. Tables are automatically created on startup.

### Production (PostgreSQL)
For production, set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

### Database Migrations

The app includes Alembic for database migrations:

```bash
# Initialize migrations (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

Set these environment variables in production:

```bash
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:password@localhost/dbname"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export CORS_ORIGINS="https://yourdomain.com"
```

### Docker Support

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📁 Project Structure

```
message/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   └── routers/
│       ├── __init__.py
│       ├── users.py         # User management endpoints
│       ├── connections.py   # Connection management endpoints
│       └── messages.py      # Messaging endpoints
├── alembic/                 # Database migrations
│   ├── env.py
│   └── script.py.mako
├── requirements.txt          # Python dependencies
├── alembic.ini             # Alembic configuration
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

### Database Configuration

The app automatically detects the database type:
- **SQLite**: Used for local development
- **PostgreSQL**: Used when `DATABASE_URL` starts with `postgresql://`

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the correct directory and virtual environment is activated
2. **Database Errors**: Check if the database file exists and has proper permissions
3. **JWT Errors**: Verify the `SECRET_KEY` environment variable is set
4. **WebSocket Issues**: Ensure the token is passed as a query parameter

### Logs

Enable debug logging by setting the log level:

```bash
uvicorn app.main:app --reload --log-level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code comments for implementation details

---

**Happy Coding! 🚀**
