from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Record
from .serializers import RecordSerializer
from apps.users.permissions import IsAnalystOrAdmin,IsRecordAccessPermission


class InsightsView(APIView):
    permission_classes=[IsAnalystOrAdmin]
    
    def get(self, request):
        return Response({
            "message": "Insights accessed successfully",
            "username": request.user.username,
            "role": request.user.role,
            "insights": {
                "top_category": "No data yet",
                "highest_expense": 0,
                "monthly_trend": "No data yet"
            }
        })

class RecordListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsRecordAccessPermission]
    
    def get(self,request):
        if request.user.role == "admin":
            records = Record.objects.all()
        else:
            records = Record.objects.filter(user=request.user).order_by("-created_at")
        category = request.query_params.get("category")
        record_type = request.query_params.get("record_type")
        date = request.query_params.get("date")
        
        if category:
            records = records.filter(category=category)
            
        if record_type:
            records = records.filter(record_type=record_type)
            
        if date:
            records = records.filter(date=date)
            
        serializer = RecordSerializer(records, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = RecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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