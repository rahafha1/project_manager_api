from django.urls import path
from .views_auth import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_project_task import ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')


urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]


