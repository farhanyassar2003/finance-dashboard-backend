from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from apps.records.models import Record
from apps.dashboard.serializers import RecentTransactionSerializer


class DashboardService:
    RECENT_TRANSACTIONS_LIMIT = 5

    @classmethod
    def get_filtered_records(cls, user, validated_data):
        records = Record.objects.filter(user=user)

        start_date = validated_data.get("start_date")
        end_date = validated_data.get("end_date")

        if start_date:
            records = records.filter(date__gte=start_date)

        if end_date:
            records = records.filter(date__lte=end_date)

        return records

    @staticmethod
    def get_total_by_type(records, record_type):
        total = records.filter(record_type=record_type).aggregate(
            total=Sum("amount")
        )["total"]

        return total or Decimal("0.00")

    @classmethod
    def get_summary_data(cls, records):
        total_income = cls.get_total_by_type(records, "income")
        total_expense = cls.get_total_by_type(records, "expense")

        return {
            "total_records": records.count(),
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
        }

    @staticmethod
    def get_category_breakdown(records):
        category_data = (
            records.values("category")
            .annotate(total=Sum("amount"))
            .order_by("category")
        )

        return {
            item["category"]: item["total"] or Decimal("0.00")
            for item in category_data
        }

    @staticmethod
    def get_monthly_trend(records):
        trend_queryset = (
            records.annotate(month=TruncMonth("date"))
            .values("month", "record_type")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        monthly_data = {}

        for item in trend_queryset:
            month_key = item["month"].strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "income": Decimal("0.00"),
                    "expense": Decimal("0.00"),
                }

            if item["record_type"] == "income":
                monthly_data[month_key]["income"] = item["total"] or Decimal("0.00")
            elif item["record_type"] == "expense":
                monthly_data[month_key]["expense"] = item["total"] or Decimal("0.00")

        return list(monthly_data.values())

    @classmethod
    def get_recent_transactions(cls, records):
        recent_transactions = records.order_by("-date", "-id")[
            :cls.RECENT_TRANSACTIONS_LIMIT
        ]
        serializer = RecentTransactionSerializer(recent_transactions, many=True)
        return serializer.data

    @classmethod
    def build_dashboard_data(cls, user, validated_data):
        records = cls.get_filtered_records(user, validated_data)

        return {
            **cls.get_summary_data(records),
            "category_breakdown": cls.get_category_breakdown(records),
            "monthly_trend": cls.get_monthly_trend(records),
            "recent_transactions": cls.get_recent_transactions(records),
        }