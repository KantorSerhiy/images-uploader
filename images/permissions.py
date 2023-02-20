from rest_framework.permissions import BasePermission


class PlanIsSet(BasePermission):
    message = 'This page is not allowed.'

    def has_permission(self, request, view):
        if request.user.plan:
            return True
        return False


class BinaryImageCreate(BasePermission):
    message = 'This page is not allowed.'

    def has_permission(self, request, view):
        if request.user.plan.download_binary_image_link:
            return True
