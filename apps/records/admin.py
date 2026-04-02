from django.contrib import admin
from .models import Record

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "amount", "record_type", "category", "date", "created_at")
    list_filter = ("record_type", "category", "date")
    search_fields = ("title", "user__username", "description")