from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from .serializers import RegisterSerializer,LoginSerializer


class RegisterView(APIView):
    
    """
    Public endpoint for registering a new user.
    Newly registered users are assigned the default 'viewer' role.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
        {
            "message": "User registered successfully.",
            "data": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "department": user.department,
                "is_active": user.is_active,
            }
        },
        status=status.HTTP_201_CREATED,
    )

class LoginView(APIView):
    
    """
    Public endpoint for authenticating a user and returning JWT tokens.
    """ 
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        return Response(
            {
                "message": "Login successful.",
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "department": user.department,
                        "is_active": user.is_active,
                    },
                    "tokens": {
                        "refresh": serializer.validated_data["refresh"],
                        "access": serializer.validated_data["access"],
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

