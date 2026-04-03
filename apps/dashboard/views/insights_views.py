from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.users.permissions import IsAnalystOrAdmin
from apps.dashboard.services.insights_services import InsightsService


class InsightsView(APIView):
    permission_classes = [IsAuthenticated, IsAnalystOrAdmin]

    def get(self, request):
        insights_data = InsightsService.build_insights_data(
            user=request.user,
            query_params=request.query_params,
        )

        return Response(
            {
                "message": "Insights fetched successfully.",
                "username": request.user.username,
                "role": request.user.role,
                "filter_username": request.query_params.get("username"),
                "data": insights_data,
            },
            status=status.HTTP_200_OK,
        )