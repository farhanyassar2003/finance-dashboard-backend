from rest_framework import serializers
from apps.records.models import Record


class DashboardFilterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def validate_username(self, value):
        return value.strip()

    def to_internal_value(self, data):
        allowed_fields = {"username", "start_date", "end_date"}
        errors = {}

        for field in data.keys():
            if field not in allowed_fields:
                errors[field] = ["This query parameter is not allowed."]

        if errors:
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"date_range": ["start_date cannot be greater than end_date."]}
            )

        return attrs


class DashboardSummarySerializer(serializers.Serializer):
    total_records = serializers.IntegerField(read_only=True)

    total_income = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    total_expense = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    category_breakdown = serializers.DictField(read_only=True)

    monthly_trend = serializers.ListField(read_only=True)

    weekly_trend = serializers.ListField(read_only=True)

    recent_transactions = serializers.ListField(read_only=True)


class RecentTransactionSerializer(serializers.ModelSerializer):
    record_type_display = serializers.CharField(
        source="get_record_type_display",
        read_only=True,
    )
    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    class Meta:
        model = Record
        fields = [
            "id",
            "title",
            "amount",
            "record_type",
            "record_type_display",
            "category",
            "category_display",
            "date",
            "description",
            "created_at",
        ]
        read_only_fields = fields


class InsightsFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    category = serializers.ChoiceField(
        choices=Record.CATEGORY_CHOICES,
        required=False,
    )
    record_type = serializers.ChoiceField(
        choices=Record.RECORD_TYPE_CHOICES,
        required=False,
    )
    username = serializers.CharField(required=False, allow_blank=False)
    
    def to_internal_value(self, data):
        allowed_fields = {
            "start_date",
            "end_date",
            "category",
            "record_type",
            "username",
        }

        errors = {}

        for field in data.keys():
            if field not in allowed_fields:
                errors[field] = ["This query parameter is not allowed."]

        if errors:
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)


    def validate_username(self, value):
        return value.strip()

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"date_range": ["start_date cannot be greater than end_date."]}
            )

        return attrs