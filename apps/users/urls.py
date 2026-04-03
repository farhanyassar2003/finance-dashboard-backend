from django.urls import path
from .views import UserListView, UpdateUserRoleView, ToggleUserStatusView

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:user_id>/role/", UpdateUserRoleView.as_view(), name="update-user-role"),
    path("<int:user_id>/status/", ToggleUserStatusView.as_view(), name="toggle-user-status"),
]