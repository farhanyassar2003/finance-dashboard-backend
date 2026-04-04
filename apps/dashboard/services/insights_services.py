from decimal import Decimal

from django.db.models import Avg, Case, DecimalField, Sum, When
from django.db.models.functions import TruncMonth
from rest_framework.exceptions import ValidationError

from apps.records.models import Record
from apps.users.models import User


class InsightsService:
    TOP_EXPENSE_CATEGORIES_LIMIT = 5

    @staticmethod
    def get_filtered_records(user, validated_data):
        username = validated_data.get("username")
        start_date = validated_data.get("start_date")
        end_date = validated_data.get("end_date")
        category = validated_data.get("category")
        record_type = validated_data.get("record_type")

        if user.role == "analyst":
            if username:
                raise ValidationError(
                    {"username": ["Analysts are not allowed to filter by username."]}
                )
            records = Record.objects.filter(user=user)

        elif user.role == "admin":
            records = Record.objects.all()

            if username:
                try:
                    target_user = User.objects.get(username__iexact=username)
                except User.DoesNotExist:
                    raise ValidationError(
                        {"username": ["User with this username does not exist."]}
                    )

                records = records.filter(user=target_user)

        else:
            raise ValidationError(
                {"detail": ["You are not allowed to access insights."]}
            )

        if start_date:
            records = records.filter(date__gte=start_date)

        if end_date:
            records = records.filter(date__lte=end_date)

        if category:
            records = records.filter(category=category)

        if record_type:
            records = records.filter(record_type=record_type)

        return records

    @staticmethod
    def get_total_by_type(records, record_type):
        total = records.filter(record_type=record_type).aggregate(
            total=Sum("amount")
        )["total"]
        return total or Decimal("0.00")

    @staticmethod
    def get_average_by_type(records, record_type):
        average = records.filter(record_type=record_type).aggregate(
            avg=Avg("amount")
        )["avg"]
        return average or Decimal("0.00")

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
    def get_monthly_trend(records):
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
            .order_by("month")
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
    def get_top_expense_categories(cls, records):
        top_categories = (
            records.filter(record_type="expense")
            .values("category")
            .annotate(total=Sum("amount"))
            .order_by("-total", "category")[:cls.TOP_EXPENSE_CATEGORIES_LIMIT]
        )

        return [
            {
                "category": item["category"],
                "total": item["total"] or Decimal("0.00"),
            }
            for item in top_categories
        ]

    @classmethod
    def build_insights_data(cls, user, validated_data):
        records = cls.get_filtered_records(user, validated_data)
        record_type = validated_data.get("record_type")
        summary_data = cls.get_summary_data(records)

        data = {
            "total_records": summary_data["total_records"],
            "balance": summary_data["balance"],
            "monthly_trend": cls.get_monthly_trend(records),
        }

        if record_type != "expense":
            data["total_income"] = summary_data["total_income"]
            data["average_income"] = cls.get_average_by_type(records, "income")

        if record_type != "income":
            data["total_expense"] = summary_data["total_expense"]
            data["average_expense"] = cls.get_average_by_type(records, "expense")
            data["category_breakdown"] = cls.get_category_breakdown(records)
            data["top_expense_categories"] = cls.get_top_expense_categories(records)

        return data