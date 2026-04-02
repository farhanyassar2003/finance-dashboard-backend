from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import RegisterSerializer,LoginSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "department": user.department,
                        "is_active": user.is_active,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError:
            return Response(
                {
                    "success": False,
                    "message": "User with this username or email already exists",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Internal server error",
                    "error": str(e),  
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
class LoginView(APIView):
    authentication_classes=[]
    permission_classes=[]
    
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user=serializer.validated_data["user"]
            
            return Response(
                {
                    "message": "Login successful.",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        "department": user.department,
                    },
                    "refresh": serializer.validated_data["refresh"],
                    "access": serializer.validated_data["access"],
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Login failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        
class TestProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "You are authenticated",
            "username": request.user.username,
            "role": request.user.role,
        })
            