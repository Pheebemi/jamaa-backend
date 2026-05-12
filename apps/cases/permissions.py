from rest_framework.permissions import BasePermission


class IsOrgAdminOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('super_admin', 'org_admin')


class CanViewSensitiveCase(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_sensitive:
            return True
        user = request.user
        if user.role in ('super_admin', 'org_admin'):
            return True
        if str(obj.assigned_to_id) == str(user.id):
            return True
        return False
