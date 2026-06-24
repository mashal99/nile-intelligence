from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def compute_daily_snapshots():
    from .services import MarketSnapshotService
    from datetime import date

    area_count = MarketSnapshotService.compute_daily_snapshot(date.today())
    compound_count = MarketSnapshotService.compute_compound_snapshots(date.today())
    logger.info(f'Snapshots: {area_count} area, {compound_count} compound')
    return {'areas': area_count, 'compounds': compound_count}


@shared_task
def generate_weekly_insights():
    from .services import MarketInsight
    from .services import MarketAnalyticsService
    from apps.ai_insights.services import AIInsightsService

    svc = AIInsightsService()
    insight = svc.generate_weekly_market_summary()
    logger.info(f'Weekly insight generated: {insight.id}')
    return insight.id
