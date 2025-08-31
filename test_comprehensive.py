#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
from datetime import date, timedelta

def test_comprehensive_api():
    """Comprehensive test of all Task Management API functionality"""
    base_url = 'http://127.0.0.1:8000/api'
    
    print("=== COMPREHENSIVE TASK MANAGEMENT API TEST ===")
    
    # Test 1: User Registration
    print("\n1. Testing User Registration...")
    register_data = {
        'username': 'testuser123',
        'password': 'securepass123',
        'password_confirm': 'securepass123',
        'email': 'testuser123@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    try:
        response = requests.post(f'{base_url}/register/', json=register_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print("Registration Result:", json.dumps(result, indent=2))
        
        if response.status_code == 201:
            token = result['data']['token']
            headers = {'Authorization': f'Token {token}'}
            
            # Test 2: Create Tasks with different priorities
            print("\n2. Testing Task Creation...")
            tasks_to_create = [
                {
                    'title': 'High Priority Task',
                    'description': 'This is urgent',
                    'due_date': str(date.today() + timedelta(days=1)),
                    'priority': 'high'
                },
                {
                    'title': 'Medium Priority Task', 
                    'description': 'This is moderate',
                    'due_date': str(date.today() + timedelta(days=3)),
                    'priority': 'medium'
                },
                {
                    'title': 'Low Priority Task',
                    'description': 'This can wait',
                    'due_date': str(date.today() + timedelta(days=7)),
                    'priority': 'low'
                }
            ]
            
            created_tasks = []
            for task_data in tasks_to_create:
                response = requests.post(f'{base_url}/tasks/', json=task_data, headers=headers)
                if response.status_code == 201:
                    task = response.json()
                    created_tasks.append(task)
                    print(f"Created task: {task['title']} (ID: {task['id']})")
                else:
                    print(f"Failed to create task: {response.status_code} - {response.text}")
            
            # Test 3: List all tasks
            print("\n3. Testing Task Listing...")
            response = requests.get(f'{base_url}/tasks/', headers=headers)
            if response.status_code == 200:
                tasks = response.json()
                print(f"Found {len(tasks)} tasks")
                for task in tasks:
                    print(f"- {task['title']} ({task['priority']}) - {task['status']}")
            
            # Test 4: Filter by priority
            print("\n4. Testing Priority Filtering...")
            response = requests.get(f'{base_url}/tasks/?priority=high', headers=headers)
            if response.status_code == 200:
                high_tasks = response.json()
                print(f"High priority tasks: {len(high_tasks)}")
            
            # Test 5: Sort by priority
            print("\n5. Testing Priority Sorting...")
            response = requests.get(f'{base_url}/tasks/?sort_by=priority', headers=headers)
            if response.status_code == 200:
                sorted_tasks = response.json()
                print("Tasks sorted by priority:")
                for task in sorted_tasks:
                    print(f"- {task['title']} ({task['priority']})")
            
            # Test 6: Sort by due date
            print("\n6. Testing Due Date Sorting...")
            response = requests.get(f'{base_url}/tasks/?sort_by=due_date', headers=headers)
            if response.status_code == 200:
                sorted_tasks = response.json()
                print("Tasks sorted by due date:")
                for task in sorted_tasks:
                    print(f"- {task['title']} (Due: {task['due_date']})")
            
            # Test 7: Mark task as complete
            if created_tasks:
                task_id = created_tasks[0]['id']
                print(f"\n7. Testing Mark Task Complete (ID: {task_id})...")
                response = requests.patch(f'{base_url}/tasks/{task_id}/toggle/', headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    print("Toggle Result:", result['message'])
                    print("Completed at:", result['data']['task']['completed_at'])
                
                # Test 8: Try to edit completed task (should fail)
                print(f"\n8. Testing Edit Restriction on Completed Task...")
                edit_data = {'title': 'Trying to edit completed task'}
                response = requests.put(f'{base_url}/tasks/{task_id}/', json=edit_data, headers=headers)
                print(f"Edit attempt status: {response.status_code}")
                if response.status_code == 400:
                    print("Edit restriction working:", response.json()['error'])
                
                # Test 9: Revert task to pending
                print(f"\n9. Testing Revert to Pending...")
                revert_data = {'status': 'pending'}
                response = requests.put(f'{base_url}/tasks/{task_id}/', json=revert_data, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    print("Revert successful, completed_at:", result['completed_at'])
            
            # Test 10: Filter completed tasks
            print("\n10. Testing Status Filtering...")
            response = requests.get(f'{base_url}/tasks/?status=completed', headers=headers)
            if response.status_code == 200:
                completed_tasks = response.json()
                print(f"Completed tasks: {len(completed_tasks)}")
            
            # Test 11: Get task statistics
            print("\n11. Testing Task Statistics...")
            response = requests.get(f'{base_url}/tasks/stats/', headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print("Task Statistics:")
                print(f"- Total: {stats['total_tasks']}")
                print(f"- Pending: {stats['pending_tasks']}")
                print(f"- Completed: {stats['completed_tasks']}")
                print(f"- Completion Rate: {stats['completion_rate']}%")
            
            print("\n=== ALL TESTS COMPLETED ===")
            
        else:
            print("Registration failed, cannot continue with other tests")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure Django server is running on port 8000")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_comprehensive_api()
