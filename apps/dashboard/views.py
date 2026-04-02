from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.users.permissions import IsViewerOrAbove
from .services import DashboardService


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsViewerOrAbove]

    def get(self, request):
        dashboard_data, error_message = DashboardService.build_dashboard_data(
            user=request.user,
            query_params=request.query_params,
        )

        if error_message:
            return Response(
                {"error": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Dashboard accessed successfully",
                "username": request.user.username,
                "role": request.user.role,
                "data": dashboard_data,
            },
            status=status.HTTP_200_OK,
        )