from decimal import Decimal
from django.db.models import Sum

from apps.records.models import Record
from apps.dashboard.serializers import RecentTransactionSerializer
from apps.dashboard.utils import validate_and_get_dates


class DashboardService:
    RECENT_TRANSACTIONS_LIMIT = 5

    @classmethod
    def get_filtered_records(cls, user, query_params):
        records = Record.objects.filter(user=user)

        start_date, end_date = validate_and_get_dates(query_params)

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

    @classmethod
    def get_recent_transactions(cls, records):
        recent_transactions = records.order_by("-date", "-id")[
            :cls.RECENT_TRANSACTIONS_LIMIT
        ]
        serializer = RecentTransactionSerializer(recent_transactions, many=True)
        return serializer.data

    @classmethod
    def build_dashboard_data(cls, user, query_params):
        records = cls.get_filtered_records(user, query_params)

        return {
            **cls.get_summary_data(records),
            "recent_transactions": cls.get_recent_transactions(records),
        }