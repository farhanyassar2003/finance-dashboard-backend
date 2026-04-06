from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
import re

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=150)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=150)
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, min_length=8, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "confirm_password",
        )

    def validate_first_name(self, value):
        value = value.strip()
        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError(
                "First name should contain only letters."
            )
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError(
                "Last name should contain only letters."
            )
        return value

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username is required."
            )

        if len(value) < 4:
            raise serializers.ValidationError(
                "Username must be at least 4 characters long."
            )

        if len(value) > 150:
            raise serializers.ValidationError(
                "Username must not exceed 150 characters."
            )

        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username can contain only letters, numbers, and underscores."
            )

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        return value

    def validate_password(self, value):
        if " " in value:
            raise serializers.ValidationError(
                "Password should not contain spaces."
            )

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

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\];']", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value

    def validate(self, attrs):
        errors = {}

        if "role" in self.initial_data:
            errors["role"] = [
                "You are not allowed to set role during registration."
            ]

        if "department" in self.initial_data:
            errors["department"] = [
                "You are not allowed to set department during registration."
            ]

        allowed_fields = set(self.fields.keys())
        received_fields = set(self.initial_data.keys())
        extra_fields = received_fields - allowed_fields - {"role", "department"}

        if extra_fields:
            errors.update(
                {field: ["This field is not allowed."] for field in extra_fields}
            )

        if attrs.get("password") != attrs.get("confirm_password"):
            errors["confirm_password"] = ["Passwords do not match."]

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)

        return User.objects.create_user(
            username=validated_data["username"].strip(),
            email=validated_data["email"].strip().lower(),
            password=validated_data["password"],
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
            role="viewer",
        )
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        allowed_fields = {"username", "password"}
        received_fields = set(self.initial_data.keys())
        extra_fields = received_fields - allowed_fields

        if extra_fields:
            raise serializers.ValidationError(
                {field: ["This field is not allowed."] for field in extra_fields}
            )

        username = attrs.get("username", "").strip()
        password = attrs.get("password")

        if not username:
            raise serializers.ValidationError(
                {"username": ["Username is required."]}
            )

        if not password:
            raise serializers.ValidationError(
                {"password": ["Password is required."]}
            )

        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid username or password."]}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid username or password."]}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["This account is inactive."]}
            )

        refresh = RefreshToken.for_user(user)

        attrs["user"] = user
        attrs["refresh"] = str(refresh)
        attrs["access"] = str(refresh.access_token)
        return attrs