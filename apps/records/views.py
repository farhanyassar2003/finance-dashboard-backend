from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Record
from .serializers import RecordSerializer
from apps.users.permissions import IsRecordAccessPermission

from datetime import datetime


class RecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == "admin":
            records = Record.objects.all()
        else:
            records = Record.objects.filter(user=request.user)

        category = request.query_params.get("category")
        record_type = request.query_params.get("record_type")
        date = request.query_params.get("date")

        if category:
            records = records.filter(category=category)

        if record_type:
            records = records.filter(record_type=record_type)

        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"date": "date must be in YYYY-MM-DD format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            records = records.filter(date=date)

        serializer = RecordSerializer(records, many=True)
        return Response(
            {
                "message": "Records fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admin can create records."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RecordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            record = serializer.save()
            response_serializer = RecordSerializer(record)
            return Response(
                {
                    "message": "Record created successfully.",
                    "data": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RecordDetailView(APIView):
    permission_classes = [IsAuthenticated, IsRecordAccessPermission]

    def get_object(self, pk, user):
        try:
            if user.role == "admin":
                return Record.objects.get(pk=pk)
            return Record.objects.get(pk=pk, user=user)
        except Record.DoesNotExist:
            return None

    def get(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"error": "Record not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RecordSerializer(record)
        return Response(serializer.data)

    def put(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"error": "Record not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RecordSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save(user=record.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"error": "Record not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=record.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"error": "Record not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)