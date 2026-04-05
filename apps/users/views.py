from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAdminRole
from config.pagination import StandardPagination
from .serializers import UserListSerializer, UpdateUserRoleSerializer,AdminCreateUserSerializer,UserListFilterSerializer

User = get_user_model()


class UserListView(APIView):
    permission_classes = [IsAdminRole,IsAuthenticated]

    def get(self, request):
        filter_serializer = UserListFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        filters = filter_serializer.validated_data
        users = User.objects.all().order_by("id")

        username = filters.get("username")
        role = filters.get("role")
        department = filters.get("department")
        is_active = filters.get("is_active", None)

        if username:
            users = users.filter(username__icontains=username)

        if role:
            users = users.filter(role=role)

        if department:
            users = users.filter(department=department)

        if is_active is not None:
            users = users.filter(is_active=is_active)

        paginator = StandardPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserListSerializer(paginated_users, many=True)

        return paginator.get_paginated_response(
            serializer.data,
            message="Users fetched successfully."
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