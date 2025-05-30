from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models import Project, Task, ProjectMember

class ProjectTaskAPITests(APITestCase):

    def setUp(self):
        # إنشاء مستخدمين: admin, manager, member, عضو ثاني
        self.admin = User.objects.create_user(username='admin', password='adminpass')
        self.manager = User.objects.create_user(username='manager', password='managerpass')
        self.member = User.objects.create_user(username='member', password='memberpass')
        self.other_member = User.objects.create_user(username='other', password='otherpass')

        # تسجيل دخول المستخدمين للحصول على التوكن
        def get_token(username, password):
            response = self.client.post(reverse('token_obtain_pair'), {'username': username, 'password': password})
            return response.data['access']

        self.admin_token = get_token('admin', 'adminpass')
        self.manager_token = get_token('manager', 'managerpass')
        self.member_token = get_token('member', 'memberpass')
        self.other_member_token = get_token('other', 'otherpass')

        # إنشاء مشروع من قبل manager
        self.project = Project.objects.create(name='Test Project', description='Desc', manager=self.manager)
        ProjectMember.objects.create(project=self.project, user=self.member)

        # مشروع أنشأه العضو member ليصبح مانجر عليه
        self.member_project = Project.objects.create(name='Member Project', description='Member Desc', manager=self.member)

        # مهمة داخل المشروع الأصلي
        self.task = Task.objects.create(
            project=self.project,
            title="Manager Task",
            description="Task by manager",
            assigned_to=self.member,
            status="todo",
            due_date="2025-06-01"
        )

    # ======= اختبارات من الكود القديم =======

    def test_member_can_create_own_project_and_becomes_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        url = reverse('project-list')
        data = {
            "name": "Member's New Project",
            "description": "Desc"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # المستخدم الذي أنشأ المشروع يجب أن يكون هو المدير
        self.assertEqual(response.data['manager']['id'], self.member.id)

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

    # ======= اختبارات إضافية تغطي صلاحيات، البحث، التصفية =======

    def test_only_manager_can_update_project(self):
        url = reverse('project-detail', args=[self.project.id])

        # محاولة تعديل من عضو غير مدير
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.patch(url, {'description': 'Attempt update'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # محاولة تعديل من مدير المشروع
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.patch(url, {'description': 'Updated description'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_only_manager_can_delete_project(self):
        url = reverse('project-detail', args=[self.project.id])

        # محاولة حذف من عضو غير مدير
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # محاولة حذف من مدير المشروع
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_sees_only_own_projects(self):
        # عضو "other" لا يملك أي مشروع أو عضوية
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # العضو member يرى مشروعه كمانجر وكمشارك
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.get(url)
        project_ids = [proj['id'] for proj in response.data]
        self.assertIn(self.project.id, project_ids)
        self.assertIn(self.member_project.id, project_ids)

    def test_only_manager_or_assigned_can_update_task(self):
        url = reverse('task-detail', args=[self.task.id])

        # عضو غير مدير ومش معين
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        response = self.client.patch(url, {'title': 'Hack Task'})
        # تعديل هنا لقبول 403 أو 404
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # عضو معين للمهمة
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        response = self.client.patch(url, {'title': 'Updated by assigned'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by assigned')

        # مدير المشروع
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.patch(url, {'title': 'Updated by manager'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by manager')

    def test_only_manager_or_assigned_can_delete_task(self):
        url = reverse('task-detail', args=[self.task.id])

        # عضو غير مخول
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        response = self.client.delete(url)
        # تعديل هنا لقبول 403 أو 404
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # العضو المعين
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

        # مدير المشروع
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.delete(reverse('task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_member_cannot_see_tasks(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.other_member_token)
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_member_cannot_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.member_token)
        url = reverse('task-list')
        data = {
            "project": self.project.id,
            "title": "Fail Task Creation",
            "description": "Should not allow",
            "assigned_to": self.member.id,
            "status": "todo",
            "due_date": "2025-06-01"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_tasks_by_title(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        # إنشاء مهمة مختلفة
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

    def test_filter_tasks_by_status(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        # مهمة بحالة 'done'
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

    def test_access_without_token(self):
        self.client.credentials()  # إزالة التوثيق
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

