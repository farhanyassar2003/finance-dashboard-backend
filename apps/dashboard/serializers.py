from rest_framework import serializers
from apps.records.models import Record

class DashboardSummarySerializer(serializers.Serializer):
    total_records = serializers.IntegerField(read_only=True)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


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