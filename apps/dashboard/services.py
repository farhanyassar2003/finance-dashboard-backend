from datetime import datetime
from decimal import Decimal

from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import TruncMonth

from apps.records.models import Record
from .serializers import RecentTransactionSerializer


class DashboardService:
    RECENT_TRANSACTIONS_LIMIT = 5

    @staticmethod
    def parse_date(date_string):
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    @classmethod
    def get_filtered_records(cls, user, query_params):
        records = Record.objects.filter(user=user)

        start_date_str = query_params.get("start_date")
        end_date_str = query_params.get("end_date")

        start_date = None
        end_date = None

        if start_date_str:
            start_date = cls.parse_date(start_date_str)
            if not start_date:
                return None, "start_date must be in YYYY-MM-DD format"

        if end_date_str:
            end_date = cls.parse_date(end_date_str)
            if not end_date:
                return None, "end_date must be in YYYY-MM-DD format"

        if start_date and end_date and start_date > end_date:
            return None, "start_date cannot be greater than end_date"

        if start_date:
            records = records.filter(date__gte=start_date)

        if end_date:
            records = records.filter(date__lte=end_date)

        return records, None

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

    @classmethod
    def get_recent_transactions(cls, records):
        recent_transactions = records.order_by("-date", "-id")[
            : cls.RECENT_TRANSACTIONS_LIMIT
        ]
        serializer = RecentTransactionSerializer(recent_transactions, many=True)
        return serializer.data

    @staticmethod
    def get_category_summary(records):
        category_data = (
            records.filter(record_type="expense")
            .values("category")
            .annotate(total=Sum("amount"))
            .order_by("category")
        )

        return {
            item["category"]: item["total"] or Decimal("0.00")
            for item in category_data
        }

    @staticmethod
    def get_monthly_summary(records):
        monthly_data = (
            records.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
                income=Sum(
                    Case(
                        When(record_type="income", then="amount"),
                        default=Decimal("0.00"),
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    )
                ),
                expense=Sum(
                    Case(
                        When(record_type="expense", then="amount"),
                        default=Decimal("0.00"),
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    )
                ),
            )
            .order_by("-month")
        )

        return [
            {
                "month": item["month"].strftime("%Y-%m") if item["month"] else None,
                "income": item["income"] or Decimal("0.00"),
                "expense": item["expense"] or Decimal("0.00"),
            }
            for item in monthly_data
        ]

    @classmethod
    def build_dashboard_data(cls, user, query_params):
        records, error_message = cls.get_filtered_records(user, query_params)

        if error_message:
            return None, error_message

        data = {
            **cls.get_summary_data(records),
            "category_summary": cls.get_category_summary(records),
            "recent_transactions": cls.get_recent_transactions(records),
            "monthly_summary": cls.get_monthly_summary(records),
        }

        return data, None