from django.db import models
from django.conf import settings


class Report(models.Model):
    class ReportType(models.TextChoices):
        WEEKLY_MARKET = 'weekly_market', 'Weekly Market Report'
        MONTHLY_MARKET = 'monthly_market', 'Monthly Market Report'
        AREA_ANALYSIS = 'area_analysis', 'Area Analysis'
        DEVELOPER_PROFILE = 'developer_profile', 'Developer Profile'
        COMPOUND_COMPARISON = 'compound_comparison', 'Compound Comparison'
        INVESTMENT_BRIEF = 'investment_brief', 'Investment Brief'
        CUSTOM = 'custom', 'Custom Report'

    class ReportStatus(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        GENERATING = 'generating', 'Generating'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class ExportFormat(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EXCEL = 'excel', 'Excel'
        JSON = 'json', 'JSON'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=500)
    report_type = models.CharField(max_length=30, choices=ReportType.choices)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.QUEUED)

    # Report scope
    area = models.ForeignKey('properties.Area', on_delete=models.SET_NULL, null=True, blank=True)
    developer = models.ForeignKey('properties.Developer', on_delete=models.SET_NULL, null=True, blank=True)
    compounds = models.ManyToManyField('properties.Compound', blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    parameters = models.JSONField(default=dict)

    # Output
    export_format = models.CharField(max_length=10, choices=ExportFormat.choices, default=ExportFormat.PDF)
    file_url = models.URLField(blank=True)
    file_size_kb = models.PositiveIntegerField(null=True, blank=True)

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)

    celery_task_id = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.title} ({self.report_type})'


class ReportTemplate(models.Model):
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    template_config = models.JSONField(default=dict)
    is_system = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report_templates'


class ScheduledReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_reports')
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=30)
    export_format = models.CharField(max_length=10, default='pdf')
    parameters = models.JSONField(default=dict)
    cron_expression = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    celery_beat_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheduled_reports'
