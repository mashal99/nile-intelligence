from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Report
from .tasks import generate_report_task
from . import serializers as s


class ReportListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return s.CreateReportSerializer
        return s.ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = s.CreateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        report = Report.objects.create(
            user=request.user,
            title=d['title'],
            report_type=d['report_type'],
            export_format=d.get('export_format', 'pdf'),
            area=d.get('area'),
            developer=d.get('developer'),
            date_from=d.get('date_from'),
            date_to=d.get('date_to'),
            parameters=d.get('parameters', {}),
        )

        task = generate_report_task.delay(report.id)
        report.celery_task_id = task.id
        report.save(update_fields=['celery_task_id'])

        return Response(s.ReportSerializer(report).data, status=status.HTTP_202_ACCEPTED)


class ReportDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = s.ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)


class ReportDownloadView(APIView):
    def get(self, request, pk):
        try:
            report = Report.objects.get(pk=pk, user=request.user, status=Report.ReportStatus.COMPLETED)
            return Response({'download_url': report.file_url})
        except Report.DoesNotExist:
            return Response({'detail': 'Report not found or not ready.'}, status=status.HTTP_404_NOT_FOUND)
