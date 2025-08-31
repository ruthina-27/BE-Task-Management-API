# Task Management API Documentation

## Overview
Simple REST API for managing tasks with user authentication. Built with Django REST Framework for learning purposes.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
The API supports both Token and JWT authentication:

### Token Authentication (Legacy)
```http
Authorization: Token your_token_here
```

### JWT Authentication (Recommended)
```http
Authorization: Bearer your_jwt_token_here
```

## Authentication Endpoints

### User Registration
**POST** `/api/register/`

Register a new user account.

**Request Body:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "message": "Registration successful!",
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2025-08-24T13:00:00Z"
    },
    "token": "your_token_here"
}
```

### User Login
**POST** `/api/login/`

Login with existing credentials.

**Request Body:**
```json
{
    "username": "newuser",
    "password": "password123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful!",
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "user@example.com"
    },
    "token": "your_token_here"
}
```

### JWT Token Endpoints
**POST** `/api/token/` - Get JWT tokens
**POST** `/api/token/refresh/` - Refresh JWT token

## Task Management Endpoints

### List/Create Tasks
**GET** `/api/tasks/`

Get all tasks for the authenticated user with optional filtering.

**Query Parameters:**
- `status` - Filter by status (`pending`, `completed`)
- `priority` - Filter by priority (`low`, `medium`, `high`)
- `due_date` - Filter by due date (YYYY-MM-DD)
- `overdue` - Filter overdue tasks (`true`, `false`)
- `due_today` - Filter tasks due today (`true`, `false`)
- `search` - Search in title and description

**Response (200 OK):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Complete project",
            "description": "Finish the task management API",
            "due_date": "2025-08-25",
            "priority": "high",
            "status": "pending",
            "created_at": "2025-08-24T13:00:00Z",
            "updated_at": "2025-08-24T13:00:00Z",
            "completed_at": null,
            "user": {
                "id": 1,
                "username": "newuser"
            },
            "is_overdue": false
        }
    ]
}
```

**POST** `/api/tasks/`

Create a new task.

**Request Body:**
```json
{
    "title": "New Task",
    "description": "Task description",
    "due_date": "2025-08-25",
    "priority": "medium"
}
```

### Task Detail Operations
**GET** `/api/tasks/{id}/` - Get specific task
**PUT** `/api/tasks/{id}/` - Update task (not allowed if completed)
**DELETE** `/api/tasks/{id}/` - Delete task

### Toggle Task Status
**PATCH** `/api/tasks/{id}/toggle/`

Toggle task between pending and completed status.

**Response (200 OK):**
```json
{
    "message": "Task marked as completed!",
    "task": {
        "id": 1,
        "title": "Complete project",
        "status": "completed",
        "completed_at": "2025-08-24T13:30:00Z"
    }
}
```

### Task Statistics
**GET** `/api/tasks/stats/`

Get task statistics for the current user.

**Response (200 OK):**
```json
{
    "total_tasks": 10,
    "pending_tasks": 6,
    "completed_tasks": 4,
    "overdue_tasks": 2,
    "due_today": 1,
    "priority_breakdown": {
        "high": 3,
        "medium": 5,
        "low": 2
    },
    "completion_rate": 40.0
}
```

### Bulk Operations
**PATCH** `/api/tasks/bulk/update/` - Update multiple tasks
**DELETE** `/api/tasks/bulk/delete/` - Delete multiple tasks

## User Profile Endpoints

### Get/Update Profile
**GET** `/api/profile/` - Get current user profile
**PUT** `/api/profile/` - Update user profile

### Change Password
**POST** `/api/profile/change-password/`

**Request Body:**
```json
{
    "old_password": "oldpass123",
    "new_password": "newpass123",
    "confirm_password": "newpass123"
}
```

### Delete Account
**DELETE** `/api/profile/delete/`

Permanently delete user account and all associated tasks.

## Error Responses

### 400 Bad Request
```json
{
    "error": "Validation failed",
    "details": {
        "due_date": ["Due date cannot be in the past!"]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
    "error": "Task not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Server error occurred",
    "message": "Detailed error message"
}
```

## Task Model Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title (max 200 chars) |
| description | text | No | Task description |
| due_date | date | Yes | When task is due (YYYY-MM-DD) |
| priority | string | No | Priority level (low/medium/high) |
| status | string | No | Task status (pending/completed) |
| completed_at | datetime | No | When task was completed |

## Business Rules

1. **Task Ownership**: Users can only access their own tasks
2. **Completed Task Editing**: Completed tasks cannot be edited unless status is reverted to pending
3. **Due Date Validation**: Due dates cannot be in the past
4. **Unique Titles**: Task titles must be unique per user
5. **Completion Timestamp**: Automatically set when task is marked complete

## Interactive Documentation

Visit these URLs when the server is running:
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

## Example Usage

### Complete Workflow
```bash
# 1. Register user
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"pass123","password_confirm":"pass123"}'

# 2. Create task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Django","due_date":"2025-08-25","priority":"high"}'

# 3. List tasks
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Token your_token_here"

# 4. Mark task complete
curl -X PATCH http://localhost:8000/api/tasks/1/toggle/ \
  -H "Authorization: Token your_token_here"
```
