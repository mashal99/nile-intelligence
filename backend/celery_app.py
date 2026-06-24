import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('nile_intelligence')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Market snapshots — runs at midnight Cairo time
    'compute-market-snapshots-daily': {
        'task': 'apps.market.tasks.compute_daily_snapshots',
        'schedule': crontab(hour=0, minute=5),
    },
    # Monitoring checks — every 30 minutes
    'check-monitoring-rules': {
        'task': 'apps.monitoring.tasks.check_monitoring_rules',
        'schedule': crontab(minute='*/30'),
    },
    # Detect market events — every hour
    'detect-market-events': {
        'task': 'apps.monitoring.tasks.detect_market_events',
        'schedule': crontab(minute=0),
    },
    # Scraping jobs — aqarmap every 4 hours
    'scrape-aqarmap': {
        'task': 'apps.properties.tasks.run_spider',
        'schedule': crontab(minute=0, hour='*/4'),
        'args': ['aqarmap'],
    },
    # nawy every 6 hours
    'scrape-nawy': {
        'task': 'apps.properties.tasks.run_spider',
        'schedule': crontab(minute=30, hour='*/6'),
        'args': ['nawy'],
    },
    # Scheduled reports
    'run-scheduled-reports': {
        'task': 'apps.reports.tasks.generate_scheduled_reports',
        'schedule': crontab(minute=0, hour=6),
    },
    # Weekly AI summary — every Monday at 7am
    'generate-weekly-ai-summary': {
        'task': 'apps.market.tasks.generate_weekly_insights',
        'schedule': crontab(hour=7, minute=0, day_of_week=1),
    },
}
