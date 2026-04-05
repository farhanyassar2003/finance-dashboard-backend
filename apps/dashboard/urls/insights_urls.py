from django.urls import path
from apps.dashboard.views.insights_views import InsightsView

urlpatterns = [
    path("", InsightsView.as_view(), name="insights"),
]