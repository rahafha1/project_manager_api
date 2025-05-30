import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    due_date = django_filters.DateFilter(field_name='due_date')
    project = django_filters.NumberFilter(field_name='project__id')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id')

    class Meta:
        model = Task
        fields = ['status', 'due_date', 'project', 'assigned_to']
