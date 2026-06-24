from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'report_type', 'status', 'export_format',
            'file_url', 'file_size_kb', 'error_message',
            'generated_at', 'created_at',
        ]


class CreateReportSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    report_type = serializers.ChoiceField(choices=Report.ReportType.choices)
    export_format = serializers.ChoiceField(choices=Report.ExportFormat.choices, default='pdf')
    area = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.properties.models', fromlist=['Area']).Area.objects.all(),
        required=False, allow_null=True,
    )
    developer = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.properties.models', fromlist=['Developer']).Developer.objects.all(),
        required=False, allow_null=True,
    )
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    parameters = serializers.JSONField(required=False, default=dict)
