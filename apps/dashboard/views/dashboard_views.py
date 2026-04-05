from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.users.permissions import IsViewerOrAbove
from apps.dashboard.serializers import DashboardFilterSerializer,DashboardSummarySerializer
from apps.dashboard.services.dashboard_service import DashboardService


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsViewerOrAbove]

    def get(self, request):
        filter_serializer = DashboardFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        dashboard_data = DashboardService.build_dashboard_data(
            user=request.user,
            validated_data=filter_serializer.validated_data,
        )

        response_serializer = DashboardSummarySerializer(dashboard_data)

        return Response(
            {
                "message": "Dashboard fetched successfully.",
                "username": request.user.username,
                "role": request.user.role,
                "filters": filter_serializer.validated_data,
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )