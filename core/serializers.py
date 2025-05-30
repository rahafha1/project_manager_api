from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, ProjectMember
from .models import Profile
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        # ❌ ما نعطي الدور من المستخدم - نخلي تلقائي Member
        Profile.objects.create(user=user, role='Member')
        return user

# Serializer لليوزر (مستخدمين المشروع)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Serializer للأعضاء المشاركين في المشروع
class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'user', 'joined_at']

# Serializer للمشاريع
class ProjectSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'manager', 'members', 'created_at']

# Serializer للمهام
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Task
        fields = ['id', 'project', 'title', 'description', 'assigned_to', 'status', 'due_date', 'created_at']