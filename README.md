# Task Management API

A simple Django REST API for managing tasks. Supports basic CRUD operations.

## Features
- Create, Read, Update, Delete tasks
- Django REST Framework
- Organized project structure

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
   pip install django djangorestframework
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

- `GET /tasks/` - List all tasks
- `POST /tasks/` - Create a new task
- `GET /tasks/<id>/` - Retrieve a task
- `PUT /tasks/<id>/` - Update a task
- `DELETE /tasks/<id>/` - Delete a task

## Project Structure
```
task_management/   # Django project settings
  settings.py
  urls.py

tasks/             # App for task management
  models.py
  views.py
  urls.py
  admin.py
```