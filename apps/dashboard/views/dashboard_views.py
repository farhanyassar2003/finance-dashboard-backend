from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.users.permissions import IsViewerOrAbove
from apps.dashboard.services.dashboard_service import DashboardService


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsViewerOrAbove]

    def get(self, request):
        dashboard_data = DashboardService.build_dashboard_data(
            user=request.user,
            query_params=request.query_params,
        )

        return Response(
            {
                "message": "Dashboard fetched successfully.",
                "username": request.user.username,
                "role": request.user.role,
                "data": dashboard_data,
            },
            status=status.HTTP_200_OK,
        )