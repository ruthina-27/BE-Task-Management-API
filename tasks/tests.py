from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Task
from datetime import date, timedelta

# Basic tests for Task Management API
# Testing all the main endpoints and functionality

class TaskModelTest(TestCase):
    """Test the Task model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_task_creation(self):
        """Test creating a basic task"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test description',
            due_date=date.today() + timedelta(days=1),
            priority='medium'
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.user, self.user)
    
    def test_task_str_method(self):
        """Test the string representation"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            due_date=date.today() + timedelta(days=1)
        )
        self.assertEqual(str(task), 'Test Task (testuser)')
    
    def test_is_overdue_method(self):
        """Test the is_overdue helper method"""
        # Create overdue task
        overdue_task = Task.objects.create(
            user=self.user,
            title='Overdue Task',
            due_date=date.today() - timedelta(days=1)
        )
        self.assertTrue(overdue_task.is_overdue())
        
        # Completed tasks should not be overdue
        overdue_task.status = 'completed'
        overdue_task.save()
        self.assertFalse(overdue_task.is_overdue())

class UserAuthenticationTest(APITestCase):
    """Test user registration and authentication"""
    
    def test_user_registration(self):
        """Test user can register"""
        url = reverse('api_register')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login(self):
        """Test user can login"""
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        url = reverse('api_login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class TaskAPITest(APITestCase):
    """Test Task CRUD operations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test description',
            'due_date': str(date.today() + timedelta(days=1)),
            'priority': 'high'
        }
    
    def test_create_task(self):
        """Test creating a new task"""
        url = reverse('api_task_list')
        response = self.client.post(url, self.task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().user, self.user)
    
    def test_list_tasks(self):
        """Test getting list of tasks"""
        Task.objects.create(
            user=self.user,
            title='Task 1',
            due_date=date.today() + timedelta(days=1)
        )
        Task.objects.create(
            user=self.user,
            title='Task 2',
            due_date=date.today() + timedelta(days=2)
        )
        
        url = reverse('api_task_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_update_task(self):
        """Test updating a task"""
        task = Task.objects.create(
            user=self.user,
            title='Original Title',
            due_date=date.today() + timedelta(days=1)
        )
        
        url = reverse('api_task_detail', kwargs={'pk': task.id})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Title')
    
    def test_delete_task(self):
        """Test deleting a task"""
        task = Task.objects.create(
            user=self.user,
            title='Task to Delete',
            due_date=date.today() + timedelta(days=1)
        )
        
        url = reverse('api_task_detail', kwargs={'pk': task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_toggle_task_status(self):
        """Test toggling task completion status"""
        task = Task.objects.create(
            user=self.user,
            title='Task to Toggle',
            due_date=date.today() + timedelta(days=1)
        )
        
        url = reverse('api_task_toggle', kwargs={'task_id': task.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)
    
    def test_task_filtering(self):
        """Test filtering tasks by status"""
        Task.objects.create(
            user=self.user,
            title='Pending Task',
            due_date=date.today() + timedelta(days=1),
            status='pending'
        )
        Task.objects.create(
            user=self.user,
            title='Completed Task',
            due_date=date.today() + timedelta(days=1),
            status='completed'
        )
        
        url = reverse('api_task_list')
        response = self.client.get(url + '?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Pending Task')
    
    def test_task_ownership(self):
        """Test users can only access their own tasks"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_task = Task.objects.create(
            user=other_user,
            title='Other User Task',
            due_date=date.today() + timedelta(days=1)
        )
        
        # Try to access other user's task
        url = reverse('api_task_detail', kwargs={'pk': other_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_completed_task_edit_restriction(self):
        """Test that completed tasks cannot be edited"""
        task = Task.objects.create(
            user=self.user,
            title='Completed Task',
            due_date=date.today() + timedelta(days=1),
            status='completed'
        )
        
        url = reverse('api_task_detail', kwargs={'pk': task.id})
        data = {'title': 'Try to Update'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot edit completed tasks', response.data['error'])

class TaskStatisticsTest(APITestCase):
    """Test task statistics endpoint"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_task_statistics(self):
        """Test getting task statistics"""
        # Create some test tasks
        Task.objects.create(
            user=self.user,
            title='Pending High',
            due_date=date.today() + timedelta(days=1),
            priority='high',
            status='pending'
        )
        Task.objects.create(
            user=self.user,
            title='Completed Medium',
            due_date=date.today() + timedelta(days=1),
            priority='medium',
            status='completed'
        )
        
        url = reverse('api_task_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_tasks'], 2)
        self.assertEqual(data['pending_tasks'], 1)
        self.assertEqual(data['completed_tasks'], 1)
        self.assertEqual(data['priority_breakdown']['high'], 1)
        self.assertEqual(data['priority_breakdown']['medium'], 1)
        self.assertEqual(data['completion_rate'], 50.0)
