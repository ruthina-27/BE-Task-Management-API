# Task Management API

A comprehensive Django REST API for managing tasks with user authentication, filtering, and statistics.

## Features
- User registration and authentication with token-based auth
- Complete CRUD operations for tasks
- Task filtering by status, priority, due date
- Search functionality in task titles and descriptions
- Task statistics and analytics
- User-specific task management
- Overdue task tracking

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ruthina-27/BE-Task-Management-API.git
   cd BE-Task-Management-API
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv myvenv
   myvenv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
5. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `GET /api/profile/` - Get user profile

### Tasks
- `GET /api/tasks/` - List user's tasks with filtering
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/<id>/` - Retrieve specific task
- `PUT /api/tasks/<id>/` - Update specific task
- `DELETE /api/tasks/<id>/` - Delete specific task
- `PATCH /api/tasks/<id>/toggle/` - Toggle task completion status
- `GET /api/tasks/stats/` - Get task statistics

### Query Parameters for Task List
- `status` - Filter by 'pending' or 'completed'
- `priority` - Filter by 'low', 'medium', or 'high'
- `search` - Search in title and description
- `due_date` - Filter by specific date (YYYY-MM-DD)
- `overdue` - Show overdue tasks (true/false)
- `due_today` - Show tasks due today (true/false)

## Project Structure
```
task_management/   # Django project settings
  settings.py
  urls.py

tasks/             # App for task management
  models.py        # Task model with user relationships
  serializers.py   # API serializers
  api_views.py     # REST API views
  api_urls.py      # API URL patterns
  permissions.py   # Custom permissions
  views.py         # Traditional views
  urls.py          # Traditional URL patterns
  admin.py