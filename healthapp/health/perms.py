from rest_framework import permissions

class IsReminderOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, reminder):
        return super().has_permission(request, view) and request.user == reminder.user

class IsHealthInfoOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, healthinformation):
        return super().has_permission(request, view) and request.user == healthinformation.user