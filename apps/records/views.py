from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .pagination import RecordPagination

from .models import Record
from .serializers import (
    RecordSerializer,
    RecordFilterSerializer,
    RecordCreateSerializer,
    RecordUpdateSerializer,
)
from apps.users.permissions import IsRecordAccessPermission


class RecordListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsRecordAccessPermission]

    def get_queryset(self, request):
        if request.user.role == "admin":
            return Record.objects.all().order_by("-date", "-created_at")
        return Record.objects.filter(user=request.user).order_by("-date", "-created_at")

    def get(self, request):
        records = self.get_queryset(request)

        filter_serializer = RecordFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        if "category" in filters:
            records = records.filter(category=filters["category"])

        if "record_type" in filters:
            records = records.filter(record_type=filters["record_type"])

        if "date" in filters:
            records = records.filter(date=filters["date"])

        if "amount_min" in filters:
            records = records.filter(amount__gte=filters["amount_min"])

        if "amount_max" in filters:
            records = records.filter(amount__lte=filters["amount_max"])

        if "start_date" in filters:
            records = records.filter(date__gte=filters["start_date"])

        if "end_date" in filters:
            records = records.filter(date__lte=filters["end_date"])

        paginator = RecordPagination()
        paginated_records = paginator.paginate_queryset(records, request)

        serializer = RecordSerializer(paginated_records, many=True)

        return paginator.get_paginated_response(
            {
                "message": "Records fetched successfully.",
                "data": serializer.data,
            }
        )

    def post(self, request):
        serializer = RecordCreateSerializer(
            data=request.data,
            context={"request": request},
        )
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
        serializer = RecordUpdateSerializer(
            record,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_record = serializer.save()

        return Response(
            {
                "message": "Record updated successfully.",
                "data": RecordSerializer(updated_record).data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        record = self.get_object(pk, request.user)
        serializer = RecordUpdateSerializer(
            record,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_record = serializer.save()

        return Response(
            {
                "message": "Record partially updated successfully.",
                "data": RecordSerializer(updated_record).data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        record = self.get_object(pk, request.user)
        record.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)