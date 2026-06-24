from rest_framework.permissions import BasePermission
from django.conf import settings


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user or getattr(obj, 'user', None) == request.user


class SubscriptionRequired(BasePermission):
    """
    Usage: permission_classes = [SubscriptionRequired('professional')]
    """
    def __init__(self, required_plan: str = 'professional'):
        self.required_plan = required_plan
        self.plan_hierarchy = ['free', 'professional', 'enterprise']

    def __call__(self):
        return self

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True

        user_plan = request.user.plan or 'free'
        user_level = self.plan_hierarchy.index(user_plan) if user_plan in self.plan_hierarchy else 0
        required_level = self.plan_hierarchy.index(self.required_plan) if self.required_plan in self.plan_hierarchy else 0

        return user_level >= required_level


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.role == 'admin'
        )
