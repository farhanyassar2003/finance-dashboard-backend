from django.urls import path
from apps.dashboard.views.dashboard_views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]