from django.urls import path
from .views import RecordListCreateView,RecordDetailView

urlpatterns = [
    path("", RecordListCreateView.as_view(), name="record-list-create"),
    path("<int:pk>/", RecordDetailView.as_view(), name="record-detail"),
]