# Connection Management API Documentation

## Overview
This document describes the REST API endpoints for the LinkedIn-style professional connection system. The system allows users to manage their professional network through connection requests, acceptances, and removals.

## Base URL
```
/connections
```

## Authentication
All endpoints require authentication via session token cookie (`session_token`).

## API Endpoints

### 1. Connection Statistics
**GET** `/api/stats`

Get user's connection statistics including total connections, pending requests, and network growth metrics.

**Response:**
```json
{
  "total_connections": 45,
  "pending_requests": 3,
  "sent_requests": 2,
  "mutual_connections": 12,
  "recent_connections": 8,
  "industry_distribution": {
    "Technology": 15,
    "Finance": 8,
    "Healthcare": 6
  }
}
```

### 2. Get Connections
**GET** `/api/connections`

Retrieve user's accepted connections with pagination, sorting, and filtering.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `sort_by` (string): Sort by "name", "company", "recent", or "mutual"
- `search` (string): Search term for name, title, company, or bio
- `company_filter` (string): Filter by company
- `location_filter` (string): Filter by location

**Response:**
```json
{
  "connections": [
    {
      "id": 123,
      "user": {
        "id": 456,
        "full_name": "John Doe",
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco",
        "profile_image": "profile.jpg",
        "industry": "Technology"
      },
      "connected_since": "2024-01-15T10:30:00Z",
      "connection_type": "professional"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

### 3. Get Pending Requests
**GET** `/api/pending-requests`

Retrieve pending connection requests received by the user.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "requests": [
    {
      "id": 789,
      "sender": {
        "id": 101,
        "full_name": "Jane Smith",
        "title": "Product Manager",
        "company": "Innovation Inc",
        "profile_image": "jane.jpg",
        "location": "New York"
      },
      "message": "Hi! I'd like to connect and discuss potential collaboration opportunities.",
      "created_at": "2024-01-20T14:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 3,
    "pages": 1
  }
}
```

### 4. Get Sent Requests
**GET** `/api/sent-requests`

Retrieve connection requests sent by the user.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "requests": [
    {
      "id": 456,
      "receiver": {
        "id": 202,
        "full_name": "Bob Johnson",
        "title": "Data Scientist",
        "company": "Analytics Co",
        "profile_image": "bob.jpg",
        "location": "Seattle"
      },
      "message": "Interested in connecting to discuss data science trends.",
      "created_at": "2024-01-18T09:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 2,
    "pages": 1
  }
}
```

### 5. Get Connection Suggestions
**GET** `/api/suggestions`

Get intelligent connection suggestions based on mutual connections, same company/location, and industry.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "suggestions": [
    {
      "id": 303,
      "full_name": "Alice Brown",
      "title": "UX Designer",
      "company": "Tech Corp",
      "profile_image": "alice.jpg",
      "location": "San Francisco",
      "industry": "Technology",
      "reason": "Same company",
      "mutual_count": 5
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 25,
    "pages": 2
  }
}
```

### 6. Send Connection Request
**POST** `/api/send-request`

Send a connection request to another user.

**Form Data:**
- `receiver_id` (int, required): ID of the user to send request to
- `message` (string, optional): Personal message with the request

**Response:**
```json
{
  "message": "Connection request sent successfully",
  "status": "success",
  "request_id": 789
}
```

**Error Responses:**
- `400`: Cannot send request to yourself
- `400`: Already connected with this user
- `400`: Connection request already sent
- `404`: User not found

### 7. Respond to Connection Request
**POST** `/api/respond-request`

Accept or decline a received connection request.

**Form Data:**
- `request_id` (int, required): ID of the connection request
- `response` (string, required): Either "accept" or "decline"

**Response:**
```json
{
  "message": "Connection request accepted successfully",
  "status": "success"
}
```

**Error Responses:**
- `404`: Connection request not found
- `400`: Invalid response value

### 8. Withdraw Connection Request
**POST** `/api/withdraw-request`

Withdraw a sent connection request.

**Form Data:**
- `request_id` (int, required): ID of the connection request to withdraw

**Response:**
```json
{
  "message": "Connection request withdrawn successfully",
  "status": "success"
}
```

**Error Responses:**
- `404`: Connection request not found

### 9. Cancel Connection Request
**POST** `/api/cancel-request`

Cancel a sent connection request (alternative to withdraw).

**Form Data:**
- `request_id` (int, required): ID of the connection request to cancel

**Response:**
```json
{
  "message": "Connection request cancelled successfully",
  "status": "success"
}
```

**Error Responses:**
- `404`: Connection request not found

### 10. Remove Connection
**POST** `/api/remove-connection`

Remove an existing connection (marks as removed instead of deleting).

**Form Data:**
- `connection_id` (int, required): ID of the connection to remove

**Response:**
```json
{
  "message": "Connection removed successfully",
  "status": "success"
}
```

**Error Responses:**
- `404`: Connection not found

### 11. Get User Profile
**GET** `/api/profile/{user_id}`

Get detailed user profile for connection management.

**Path Parameters:**
- `user_id` (int): ID of the user to get profile for

**Response:**
```json
{
  "id": 456,
  "full_name": "John Doe",
  "title": "Software Engineer",
  "company": "Tech Corp",
  "location": "San Francisco",
  "bio": "Passionate software engineer with 5+ years of experience...",
  "profile_image": "profile.jpg",
  "user_type": "normal",
  "is_verified": true,
  "industry": "Technology",
  "skills": "Python, JavaScript, React, Node.js",
  "experience_years": 5,
  "education": "BS Computer Science, Stanford University",
  "certifications": "AWS Certified Developer",
  "created_at": "2020-03-15T00:00:00Z",
  "connection_status": "connected",
  "mutual_connections": [
    {
      "id": 789,
      "full_name": "Jane Smith",
      "title": "Product Manager",
      "company": "Innovation Inc",
      "profile_image": "jane.jpg"
    }
  ],
  "recent_posts": [
    {
      "id": 123,
      "content": "Excited to share our latest project...",
      "post_type": "general",
      "created_at": "2024-01-20T10:00:00Z",
      "likes_count": 15
    }
  ]
}
```

### 12. Search Users and Connections
**GET** `/api/search`

Search through users and connections with various filters.

**Query Parameters:**
- `query` (string, required): Search query
- `search_type` (string): "all", "name", "company", "title", or "skills" (default: "all")
- `location` (string, optional): Filter by location
- `industry` (string, optional): Filter by industry
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "results": [
    {
      "id": 456,
      "full_name": "John Doe",
      "title": "Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco",
      "profile_image": "profile.jpg",
      "industry": "Technology",
      "connection_status": "not_connected"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

## Connection Status Values

### Friend Request Status
- `pending`: Request sent, awaiting response
- `accepted`: Request accepted, connection established
- `declined`: Request declined
- `withdrawn`: Request withdrawn by sender
- `cancelled`: Request cancelled by sender

### Connection Status
- `pending`: Connection pending (legacy)
- `accepted`: Connection active
- `declined`: Connection declined
- `removed`: Connection removed

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include a `detail` field with the error message:

```json
{
  "detail": "Connection request already sent"
}
```

## Rate Limiting

To prevent abuse, the following limits apply:
- Connection requests: 10 per hour per user
- API calls: 1000 per hour per user

## WebSocket Events (Future Enhancement)

For real-time updates, the following WebSocket events will be implemented:
- `connection_request_received`: New connection request
- `connection_request_accepted`: Request accepted
- `connection_request_declined`: Request declined
- `connection_removed`: Connection removed

## Database Schema

### Connections Table
```sql
CREATE TABLE connections (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    connected_user_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    connection_type VARCHAR(20) DEFAULT 'professional',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    accepted_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (connected_user_id) REFERENCES users(id)
);
```

### Friend Requests Table
```sql
CREATE TABLE friend_requests (
    id INTEGER PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    responded_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);
```

## Best Practices

1. **Always check connection status** before sending requests
2. **Use pagination** for large datasets
3. **Implement proper error handling** in client applications
4. **Cache connection data** when appropriate
5. **Use WebSocket events** for real-time updates when available

## Testing

Test the API endpoints using the provided Postman collection or curl commands:

```bash
# Send connection request
curl -X POST "http://localhost:8000/connections/api/send-request" \
  -H "Cookie: session_token=your_token" \
  -F "receiver_id=123" \
  -F "message=Hi! Let's connect!"

# Get connections
curl "http://localhost:8000/connections/api/connections?page=1&limit=20" \
  -H "Cookie: session_token=your_token"
```
