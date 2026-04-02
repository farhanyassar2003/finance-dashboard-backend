from django.urls import path
from .views import RegisterView,LoginView,TestProtectedView

urlpatterns = [
    path("register/",RegisterView.as_view(),name="register"),
    path("login/",LoginView.as_view(), name="login"),
    path("test-protected/", TestProtectedView.as_view()),
]