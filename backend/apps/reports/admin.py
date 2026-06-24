from django.contrib import admin
from .models import Report, ReportTemplate, ScheduledReport


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'report_type', 'status', 'export_format', 'created_at']
    list_filter = ['status', 'report_type', 'export_format']
    search_fields = ['title', 'user__email']
    readonly_fields = ['celery_task_id', 'generated_at', 'created_at']


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_system', 'created_at']
    list_filter = ['is_system', 'report_type']


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_type', 'is_active', 'next_run_at', 'last_run_at']
    list_filter = ['is_active', 'report_type']
