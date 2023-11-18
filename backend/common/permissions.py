from rest_framework import permissions, status, exceptions


class IsAuthorized(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == "SubTask":
            if request.user.team != obj.team:
                raise exceptions.PermissionDenied
        elif obj.__class__.__name__ == "Task":
            if request.user.id != obj.create_user.id:
                raise exceptions.PermissionDenied

        return True
