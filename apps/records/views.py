from datetime import datetime

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound

from .models import Record
from .serializers import RecordSerializer
from apps.users.permissions import IsRecordAccessPermission


class RecordListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsRecordAccessPermission]

    def get_queryset(self, request):
        if request.user.role == "admin":
            return Record.objects.all()
        return Record.objects.filter(user=request.user)

    def validate_filters(self, request):
        category = request.query_params.get("category")
        record_type = request.query_params.get("record_type")
        date = request.query_params.get("date")

        if category and category not in dict(Record.CATEGORY_CHOICES):
            raise ValidationError(
                {"category": ["Invalid category."]}
            )

        if record_type and record_type not in dict(Record.RECORD_TYPE_CHOICES):
            raise ValidationError(
                {"record_type": ["Invalid record type."]}
            )

        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValidationError(
                    {"date": ["Date must be in YYYY-MM-DD format."]}
                )

        return category, record_type, date

    def get(self, request):
        records = self.get_queryset(request)
        category, record_type, date = self.validate_filters(request)

        if category:
            records = records.filter(category=category)

        if record_type:
            records = records.filter(record_type=record_type)

        if date:
            records = records.filter(date=date)

        serializer = RecordSerializer(records, many=True)
        return Response(
            {
                "message": "Records fetched successfully.",
                "count": len(serializer.data),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = RecordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        record = serializer.save()

        response_serializer = RecordSerializer(record)
        return Response(
            {
                "message": "Record created successfully.",
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class RecordDetailView(APIView):
    permission_classes = [IsAuthenticated, IsRecordAccessPermission]

    def get_object(self, pk, user):
        if user.role == "admin":
            record = Record.objects.filter(pk=pk).first()
        else:
            record = Record.objects.filter(pk=pk, user=user).first()

        if not record:
            raise NotFound("Record not found.")

        return record

    def get(self, request, pk):
        record = self.get_object(pk, request.user)
        serializer = RecordSerializer(record)

        return Response(
            {
                "message": "Record fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        record = self.get_object(pk, request.user)
        serializer = RecordSerializer(
            record,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=record.user)

        return Response(
            {
                "message": "Record updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        record = self.get_object(pk, request.user)
        serializer = RecordSerializer(
            record,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=record.user)

        return Response(
            {
                "message": "Record partially updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        record = self.get_object(pk, request.user)
        record.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)