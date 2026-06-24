from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_report_task(self, report_id: int):
    from .models import Report
    from .services import ReportGeneratorService

    try:
        report = Report.objects.get(pk=report_id)
        svc = ReportGeneratorService()
        url = svc.generate(report)
        logger.info(f'Report {report_id} generated: {url}')
        return url
    except Report.DoesNotExist:
        logger.error(f'Report {report_id} not found')
        raise
    except Exception as exc:
        logger.error(f'Report {report_id} failed: {exc}')
        raise self.retry(exc=exc)


@shared_task
def generate_scheduled_reports():
    from django.utils import timezone
    from .models import ScheduledReport

    due = ScheduledReport.objects.filter(
        is_active=True,
        next_run_at__lte=timezone.now(),
    )
    for scheduled in due:
        from .models import Report
        report = Report.objects.create(
            user=scheduled.user,
            title=f'Scheduled {scheduled.report_type} - {timezone.now().date()}',
            report_type=scheduled.report_type,
            export_format=scheduled.export_format,
            parameters=scheduled.parameters,
            is_scheduled=True,
        )
        generate_report_task.delay(report.id)
        scheduled.last_run_at = timezone.now()
        scheduled.save(update_fields=['last_run_at'])
