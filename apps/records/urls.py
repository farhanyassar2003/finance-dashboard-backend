from django.urls import path
from .views import InsightsView,RecordListCreateView,RecordDetailView

urlpatterns = [
    path("insights/", InsightsView.as_view(), name="insights"),
    path("", RecordListCreateView.as_view(), name="record-list-create"),
    path("<int:pk>/", RecordDetailView.as_view(), name="record-detail"),
]