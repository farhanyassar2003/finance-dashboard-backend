from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "department",
            "is_active",
        ]


class UpdateUserRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
class UserListFilterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    department = serializers.ChoiceField(choices=User.DEPARTMENT_CHOICES, required=False)
    is_active = serializers.BooleanField(required=False)
    
    
class AdminCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "confirm_password",
            "role",
            "department",
            "is_active",
        ]

    def validate_first_name(self, value):
        value = value.strip()
        if value and not value.replace(" ", "").isalpha():
            raise serializers.ValidationError(
                "First name should contain only letters."
            )
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if value and not value.replace(" ", "").isalpha():
            raise serializers.ValidationError(
                "Last name should contain only letters."
            )
        return value

    def validate_username(self, value):
        value = value.strip()

        if len(value) < 4:
            raise serializers.ValidationError(
                "Username must be at least 4 characters long."
            )

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate_password(self, value):
        if value.isspace():
            raise serializers.ValidationError(
                "Password cannot contain only spaces."
            )

        if value.lower() == value or value.upper() == value:
            raise serializers.ValidationError(
                "Password must contain both uppercase and lowercase letters."
            )

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value

    def validate(self, attrs):
        extra_fields = set(self.initial_data.keys()) - set(self.fields.keys())
        if extra_fields:
            raise serializers.ValidationError({
                "extra_fields": [
                    f"Unexpected fields: {', '.join(extra_fields)}"
                ]
            })

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": ["Passwords do not match."]}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user