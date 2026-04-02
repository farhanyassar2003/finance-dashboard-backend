from django.contrib.auth import get_user_model,authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
import re

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    
    password=serializers.CharField(write_only=True,min_length=8)
    confirm_password=serializers.CharField(write_only=True,min_length=8)
    
    class Meta:
        model = User
        fields=(
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "confirm_password"
        )
        
    def validate_first_name(self, value):
        value = value.strip()
        if value and not value.replace(" ", "").isalpha():
            raise serializers.ValidationError("First name should contain only letters.")
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if value and not value.replace(" ", "").isalpha():
            raise serializers.ValidationError("Last name should contain only letters.")
        return value
     # Username validation
    def validate_username(self, value):
        value = value.strip()
        if len(value) < 4:
            raise serializers.ValidationError(
                "Username must be at least 4 characters long."
            )

        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username can contain only letters, numbers, and underscores."
            )

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    # Email validation
    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    # Password validation
    def validate_password(self, value):
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        return value

    # Confirm password validation
    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

    # Create user with default role
    def create(self, validated_data):
        validated_data.pop("confirm_password", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role="viewer", 
        )

        return user
    
class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self,attrs):
        username=attrs.get("username", "").strip()
        password=attrs.get("password")
        
        if not username:
            raise serializers.ValidationError({"username": "Username is required."})
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})
        
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid username or password."]}
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["This account is inactive."]}
            )
            
        refresh = RefreshToken.for_user(user)
        
        attrs["user"] =user
        attrs["refresh"]=str(refresh)
        attrs["access"] = str(refresh.access_token)
        
        return attrs