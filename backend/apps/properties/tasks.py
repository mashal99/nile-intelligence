from celery import shared_task
import logging
import subprocess

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_spider(self, spider_name: str):
    from .models import ScrapingJob
    from django.utils import timezone

    job = ScrapingJob.objects.create(
        portal=spider_name,
        status=ScrapingJob.JobStatus.RUNNING,
        celery_task_id=self.request.id,
    )

    try:
        result = subprocess.run(
            ['scrapy', 'crawl', spider_name, '-a', f'job_id={job.id}'],
            cwd='/app/scrapers',
            capture_output=True,
            text=True,
            timeout=3600,
        )

        if result.returncode == 0:
            job.status = ScrapingJob.JobStatus.COMPLETED
        else:
            job.status = ScrapingJob.JobStatus.FAILED
            job.error_log = result.stderr[-5000:]

        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'completed_at', 'error_log'])
        return job.id

    except subprocess.TimeoutExpired:
        job.status = ScrapingJob.JobStatus.FAILED
        job.error_log = 'Spider timed out after 60 minutes'
        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'completed_at', 'error_log'])
        raise
    except Exception as exc:
        job.status = ScrapingJob.JobStatus.FAILED
        job.error_log = str(exc)
        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'completed_at', 'error_log'])
        raise self.retry(exc=exc)
