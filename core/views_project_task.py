from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .permissions import IsProjectManager, IsTaskManagerOrAssignee , IsAdminOrManager 
from django.db import models
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter
from rest_framework.filters import SearchFilter



class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(models.Q(manager=user) | models.Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsProjectManager]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            models.Q(project__manager=user) | 
            models.Q(project__members=user)
        ).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:  # ✅ تم إضافة 'create'
            permission_classes = [IsAuthenticated, IsTaskManagerOrAssignee]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        # ✅ تم تعديل هذا الشرط ليسمح لأي عضو في المشروع أو المدير
        if self.request.user != project.manager and self.request.user not in project.members.all():
            raise PermissionDenied("Only the project manager or project members can create tasks.")
        serializer.save()
