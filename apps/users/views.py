from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from .permissions import IsAdminRole
from .serializers import UserListSerializer, UpdateUserRoleSerializer,AdminCreateUserSerializer,UserListFilterSerializer

User = get_user_model()


class UserListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        filter_serializer = UserListFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        filters = filter_serializer.validated_data
        users = User.objects.all()

        if "username" in filters:
            users = users.filter(username__icontains=filters["username"])

        if "role" in filters:
            users = users.filter(role=filters["role"])

        if "department" in filters:
            users = users.filter(department=filters["department"])

        if "is_active" in filters:
            users = users.filter(is_active=filters["is_active"])

        serializer = UserListSerializer(users, many=True)

        return Response(
            {
                "message": "Users fetched successfully.",
                "count": users.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class AdminCreateUserView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = AdminCreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User created successfully by admin.",
                "data": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "department": user.department,
                    "is_active": user.is_active,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UpdateUserRoleView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if request.user.id == user.id:
            raise PermissionDenied("You cannot change your own role.")

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
            raise PermissionDenied("You cannot change your own active status.")

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