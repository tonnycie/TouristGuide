from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Всеки може да чете, но само авторът може да променя или трие."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user