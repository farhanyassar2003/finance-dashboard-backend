from django.urls import path
from .views import UserManagementView,UserListView, UpdateUserRoleView, ToggleUserStatusView

urlpatterns = [
    path("user-management/", UserManagementView.as_view(), name="user-management"),
    path("users/", UserListView.as_view()),
    path("users/<int:user_id>/role/", UpdateUserRoleView.as_view()),
    path("users/<int:user_id>/status/", ToggleUserStatusView.as_view()),
]