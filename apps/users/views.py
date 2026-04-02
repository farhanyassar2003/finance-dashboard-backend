from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .permissions import IsAdminRole


User = get_user_model()

#demo
class UserManagementView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response({
            "message": "User management accessed successfully",
            "username": request.user.username,
            "role": request.user.role
        })
        
class UserListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        users = User.objects.all()

        data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            }
            for user in users
        ]

        return Response(data)
    
class UpdateUserRoleView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        new_role = request.data.get("role")

        if new_role not in ["viewer", "analyst", "admin"]:
            return Response({"error": "Invalid role"}, status=400)

        user.role = new_role
        user.save()

        return Response({
            "message": "User role updated successfully",
            "username": user.username,
            "new_role": user.role
        })
        
class ToggleUserStatusView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user.is_active = not user.is_active
        user.save()

        return Response({
            "message": "User status updated",
            "username": user.username,
            "is_active": user.is_active
        })



