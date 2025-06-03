from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models import Project, Task, ProjectMember

class ProjectTaskAPITests(APITestCase):

    def setUp(self):
        # إنشاء المستخدمين
        self.admin = User.objects.create_user(username='admin', password='adminpass')
        self.manager = User.objects.create_user(username='manager', password='managerpass')
        self.member = User.objects.create_user(username='member', password='memberpass')
        self.other_member = User.objects.create_user(username='other', password='otherpass')

        # دالة مساعدة للحصول على توكن
        def get_token(username, password):
            response = self.client.post(reverse('token_obtain_pair'), {'username': username, 'password': password})
            return response.data['access']

        self.admin_token = get_token('admin', 'adminpass')
        self.manager_token = get_token('manager', 'managerpass')
        self.member_token = get_token('member', 'memberpass')
        self.other_member_token = get_token('other', 'otherpass')

        # إنشاء المشاريع والعضويات
        self.project = Project.objects.create(name='Test Project', description='Desc', manager=self.manager)
        ProjectMember.objects.create(project=self.project, user=self.member)

        self.member_project = Project.objects.create(name='Member Project', description='Member Desc', manager=self.member)

        # إنشاء مهمة داخل المشروع
        self.task = Task.objects.create(
            project=self.project,
            title="Manager Task",
            description="Task by manager",
            assigned_to=self.member,
            status="todo",
            due_date="2025-06-01"
        )

    # ======= اختبارات إنشاء المشاريع =======
    def test_member_can_create_own_project_and_becomes_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        url = reverse('project-list')
        data = {
            "name": "Member's New Project",
            "description": "Desc"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['manager']['id'], self.member.id)

    # ======= اختبارات إنشاء المهام =======
    def test_manager_can_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        url = reverse('task-list')
        data = {
            "project": self.project.id,
            "title": "New Task",
            "description": "Task desc",
            "assigned_to": self.member.id,
            "status": "todo",
            "due_date": "2025-06-01"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_assigned_member_can_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        url = reverse('task-list')
        data = {
            "project": self.project.id,
            "title": "Task by assigned member",
            "description": "Created by member",
            "assigned_to": self.member.id,
            "status": "todo",
            "due_date": "2025-06-05"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['assigned_to'], self.member.id)

    def test_non_assigned_member_cannot_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        url = reverse('task-list')
        data = {
            "project": self.project.id,
            "title": "Invalid Task",
            "description": "Should not be created",
            "assigned_to": self.member.id,
            "status": "todo",
            "due_date": "2025-06-10"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ======= اختبارات تحديث المشاريع =======
    def test_only_manager_can_update_project(self):
        url = reverse('project-detail', args=[self.project.id])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.patch(url, {'description': 'Attempt update'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.patch(url, {'description': 'Updated description'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    # ======= اختبارات حذف المشاريع =======
    def test_only_manager_can_delete_project(self):
        url = reverse('project-detail', args=[self.project.id])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ======= اختبارات رؤية المشاريع =======
    def test_user_sees_only_own_projects(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.get(url)
        project_ids = [proj['id'] for proj in response.data]
        self.assertIn(self.project.id, project_ids)
        self.assertIn(self.member_project.id, project_ids)

    # ======= اختبارات تحديث المهام =======
    def test_only_manager_or_assigned_can_update_task(self):
        url = reverse('task-detail', args=[self.task.id])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        response = self.client.patch(url, {'title': 'Hack Task'})
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.patch(url, {'title': 'Updated by assigned'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by assigned')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.patch(url, {'title': 'Updated by manager'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by manager')

    # ======= اختبارات حذف المهام =======
    def test_only_manager_or_assigned_can_delete_task(self):
        url = reverse('task-detail', args=[self.task.id])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])

        # إعادة إنشاء المهمة للاختبار التالي
        self.task = Task.objects.create(
            project=self.project,
            title="Manager Task 2",
            description="Another task",
            assigned_to=self.member,
            status="todo",
            due_date="2025-06-01"
        )

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.delete(reverse('task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ======= اختبارات رؤية المهام =======
    def test_non_member_cannot_see_tasks(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ======= اختبارات البحث والتصفية =======
    def test_search_tasks_by_title(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        Task.objects.create(
            project=self.project,
            title="Unique Search Task",
            description="Desc",
            assigned_to=self.member,
            status="todo",
            due_date="2025-06-01"
        )
        url = reverse('task-list') + '?search=Unique'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Unique Search Task" in task['title'] for task in response.data))

    def test_search_tasks_by_description(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        Task.objects.create(
            project=self.project,
            title="Task with unique desc",
            description="This description is unique for search",
            assigned_to=self.member,
            status="todo",
            due_date="2025-06-01"
        )
        url = reverse('task-list') + '?search=unique for search'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("unique for search" in task['description'] for task in response.data))
   


    def test_filter_tasks_by_status(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        Task.objects.create(
            project=self.project,
            title="Done Task",
            description="Done desc",
            assigned_to=self.member,
            status="done",
            due_date="2025-06-01"
        )
        url = reverse('task-list') + '?status=done'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(task['status'] == 'done' for task in response.data))

    # ======= اختبارات الوصول بدون توكن =======
    def test_access_without_token(self):
        self.client.credentials()  # إزالة التوثيق
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
