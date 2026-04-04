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

        if request and request.method == "POST" and request.user.role == "admin":
            if not username:
                raise serializers.ValidationError(
                    {"username": ["Username is required for admin record creation."]}
                )

            try:
                user = User.objects.get(username__iexact=username.strip())
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"username": ["User with this username does not exist."]}
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


class RecordFilterSerializer(serializers.Serializer):
    category = serializers.ChoiceField(
        choices=Record.CATEGORY_CHOICES,
        required=False
    )
    record_type = serializers.ChoiceField(
        choices=Record.RECORD_TYPE_CHOICES,
        required=False
    )
    date = serializers.DateField(
        required=False,
        input_formats=["%Y-%m-%d"]
    )
    start_date = serializers.DateField(
        required=False,
        input_formats=["%Y-%m-%d"]
    )
    end_date = serializers.DateField(
        required=False,
        input_formats=["%Y-%m-%d"]
    )
    amount_min = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    amount_max = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )

    def validate_amount_min(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount minimum must be 0 or greater.")
        return value

    def validate_amount_max(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount maximum must be 0 or greater.")
        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        amount_min = attrs.get("amount_min")
        amount_max = attrs.get("amount_max")

        errors = {}

        if start_date and end_date and start_date > end_date:
            errors["date_range"] = ["start_date cannot be later than end_date."]

        if (
            amount_min is not None
            and amount_max is not None
            and amount_min > amount_max
        ):
            errors["amount_range"] = ["amount_min cannot be greater than amount_max."]

        if errors:
            raise serializers.ValidationError(errors)

        return attrs