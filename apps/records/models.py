from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Record(models.Model):
    RECORD_TYPE_CHOICES = (
        ("income", "Income"),
        ("expense", "Expense"),
    )

    CATEGORY_CHOICES = (
        ("salary", "Salary"),
        ("food", "Food"),
        ("transport", "Transport"),
        ("rent", "Rent"),
        ("shopping", "Shopping"),
        ("bill", "Bill"),
        ("health", "Health"),
        ("other", "Other"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="records"
    )
    title = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    record_type = models.CharField(max_length=10, choices=RECORD_TYPE_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.record_type} - {self.amount}"