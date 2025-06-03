from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProjectManager(BasePermission):
    """
    يسمح فقط لمدير المشروع بالتعديل أو الحذف.
    السماح بالقراءة للجميع الأعضاء فقط.
    """
    def has_object_permission(self, request, view, obj):
        # ✅ السماح الكامل للمشرف المطلق
        if request.user.is_superuser:
            return True
        
        # السماح بالقراءة لأي عضو في المشروع
        if request.method in SAFE_METHODS:
            return obj.manager == request.user or request.user in obj.members.all()
        
        # السماح بالتعديل والحذف فقط للمدير
        return obj.manager == request.user



class IsTaskManagerOrAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        # ✅ السماح الكامل للمشرف المطلق
        if request.user.is_superuser:
            return True

        project = obj.project
        
        if request.method in SAFE_METHODS:
            # ✅ القراءة متاحة فقط للمدير أو الأعضاء
            return project.manager == request.user or request.user in project.members.all()
        
        # ✅ التعديل أو الإنشاء متاح للمدير أو المكلّف أو أي عضو في المشروع
        return (
            project.manager == request.user or
            obj.assigned_to == request.user or
            request.user in project.members.all()  # ✅ ← هذا هو الإضافة الجديدة
        )


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        # ✅ السماح الكامل للمشرف المطلق
        if request.user.is_superuser:
            return True
        
        # السماح فقط للأدمن (staff)
        return request.user and request.user.is_authenticated and request.user.is_staff


