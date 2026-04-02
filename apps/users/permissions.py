from rest_framework.permissions import BasePermission

class IsViewerOrAbove(BasePermission):
    def has_permission(self, request, view):
        return(
            request.user.is_authenticated and
            request.user.role in ["viewer", "analyst", "admin"]
        )
class IsAnalystOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["analyst", "admin"]
        )


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "admin"
        )    
        
class IsRecordAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request.user.role in ["analyst", "admin"]

        return request.user.role == "admin"
    