from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .permissions import IsAdminRole
from .serializers import UserListSerializer, UpdateUserRoleSerializer

User = get_user_model()


class UserListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)

        return Response(
            {
                "message": "Users fetched successfully.",
                "count": users.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpdateUserRoleView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user.id == user.id:
            raise ValidationError({"detail": "You cannot change your own role."})

        serializer = UpdateUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.role = serializer.validated_data["role"]
        user.save(update_fields=["role", "updated_at"])

        return Response(
            {
                "message": "User role updated successfully.",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class ToggleUserStatusView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user.id == user.id:
            raise ValidationError(
                {"detail": "You cannot change your own active status."}
            )

        user.is_active = not user.is_active
        user.save(update_fields=["is_active", "updated_at"])

        return Response(
            {
                "message": "User status updated successfully.",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "is_active": user.is_active,
                },
            },
            status=status.HTTP_200_OK,
        )