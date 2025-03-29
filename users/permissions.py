from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class IsStudent(BasePermission):
    message = "Access denied: only students are allowed to perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.role == User.STUDENT


class IsTeacher(BasePermission):
    message = "Access denied: only teachers are allowed to perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.role == User.TEACHER


class IsAdmin(BasePermission):
    message = "Access denied: only administrators are allowed to perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAdminOrTeacher(BasePermission):
    message = "Access denied: only administrators or teachers can perform this action."

    def has_permission(self, request, view):
        user = request.user
        return user and (user.is_staff or user.role == User.TEACHER)
