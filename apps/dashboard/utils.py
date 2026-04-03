from datetime import datetime
from rest_framework.exceptions import ValidationError

from apps.records.models import Record


def parse_date(date_string, field_name):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValidationError(
            {field_name: ["Date must be in YYYY-MM-DD format."]}
        )


def validate_and_get_dates(query_params):
    start_date_str = query_params.get("start_date")
    end_date_str = query_params.get("end_date")

    start_date = None
    end_date = None

    if start_date_str:
        start_date = parse_date(start_date_str, "start_date")

    if end_date_str:
        end_date = parse_date(end_date_str, "end_date")

    if start_date and end_date and start_date > end_date:
        raise ValidationError(
            {"date_range": ["start_date cannot be greater than end_date."]}
        )

    return start_date, end_date


def validate_record_type(record_type):
    if not record_type:
        return None

    valid_record_types = dict(Record.RECORD_TYPE_CHOICES).keys()

    if record_type not in valid_record_types:
        raise ValidationError(
            {
                "record_type": [
                    f"record_type must be one of: {', '.join(valid_record_types)}."
                ]
            }
        )

    return record_type


def validate_category(category):
    if not category:
        return None

    valid_categories = dict(Record.CATEGORY_CHOICES).keys()

    if category not in valid_categories:
        raise ValidationError(
            {
                "category": [
                    f"category must be one of: {', '.join(valid_categories)}."
                ]
            }
        )

    return category