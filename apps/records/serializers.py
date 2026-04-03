from rest_framework import serializers
from apps.users.models import User
from .models import Record


class RecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Record
        fields = [
            "id",
            "user",
            "username",
            "title",
            "amount",
            "record_type",
            "category",
            "date",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        username = attrs.get("username")

        if request and request.method == "POST":
            if request.user.role == "admin":
                if not username:
                    raise serializers.ValidationError(
                        {"username": "Username is required for admin record creation."}
                    )

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise serializers.ValidationError(
                        {"username": "User with this username does not exist."}
                    )

                attrs["target_user"] = user

        return attrs

    def create(self, validated_data):
        validated_data.pop("username", None)
        user = validated_data.pop("target_user", None)

        if not user:
            request = self.context.get("request")
            user = request.user

        return Record.objects.create(user=user, **validated_data)