from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_monitoring_rules():
    """Run after every scraping job. Check all active rules against new/changed listings."""
    from django.utils import timezone
    from .models import MonitoringRule, Alert
    from apps.properties.models import PropertyListing

    rules = MonitoringRule.objects.filter(is_active=True).select_related(
        'user', 'area', 'developer', 'compound'
    )

    alerts_to_create = []

    for rule in rules:
        qs = PropertyListing.objects.all()

        if rule.area:
            qs = qs.filter(area=rule.area)
        if rule.developer:
            qs = qs.filter(developer=rule.developer)
        if rule.compound:
            qs = qs.filter(compound=rule.compound)
        if rule.property_type:
            qs = qs.filter(property_type=rule.property_type)
        if rule.min_price:
            qs = qs.filter(price__gte=rule.min_price)
        if rule.max_price:
            qs = qs.filter(price__lte=rule.max_price)

        cutoff = rule.last_triggered_at or (timezone.now() - timezone.timedelta(hours=24))
        recent_qs = qs.filter(scraped_at__gte=cutoff)

        if rule.rule_type == MonitoringRule.RuleType.NEW_LISTING:
            new_listings = recent_qs.filter(
                scraped_at__gte=cutoff,
                status='active',
            )
            for listing in new_listings[:10]:
                alerts_to_create.append(Alert(
                    rule=rule,
                    listing=listing,
                    title=f'New listing in {rule.name}',
                    message=f'{listing.title} - {listing.price:,.0f} EGP',
                    severity=Alert.AlertSeverity.MEDIUM,
                    metadata={'price': str(listing.price), 'url': listing.source_url},
                ))

        elif rule.rule_type in [MonitoringRule.RuleType.PRICE_DROP, MonitoringRule.RuleType.PRICE_INCREASE]:
            from apps.properties.models import ListingPriceHistory
            price_changes = ListingPriceHistory.objects.filter(
                listing__in=qs,
                recorded_at__gte=cutoff,
            ).select_related('listing')

            for change in price_changes[:20]:
                pct = abs(float(change.change_percent))
                if pct < float(rule.price_change_threshold_pct):
                    continue

                is_drop = change.change_percent < 0
                if rule.rule_type == MonitoringRule.RuleType.PRICE_DROP and not is_drop:
                    continue
                if rule.rule_type == MonitoringRule.RuleType.PRICE_INCREASE and is_drop:
                    continue

                direction = 'dropped' if is_drop else 'increased'
                alerts_to_create.append(Alert(
                    rule=rule,
                    listing=change.listing,
                    title=f'Price {direction} {pct:.1f}% — {rule.name}',
                    message=f'{change.listing.title}: {change.old_price:,.0f} → {change.new_price:,.0f} EGP',
                    severity=Alert.AlertSeverity.HIGH if pct > 10 else Alert.AlertSeverity.MEDIUM,
                    metadata={
                        'old_price': str(change.old_price),
                        'new_price': str(change.new_price),
                        'change_pct': str(change.change_percent),
                    },
                ))

    if alerts_to_create:
        Alert.objects.bulk_create(alerts_to_create, batch_size=100)
        MonitoringRule.objects.filter(
            pk__in=[r.pk for r in rules]
        ).update(last_triggered_at=timezone.now())

    _dispatch_alert_notifications(alerts_to_create)
    logger.info(f'Created {len(alerts_to_create)} alerts')
    return len(alerts_to_create)


def _dispatch_alert_notifications(alerts):
    from django.core.mail import send_mail
    from django.conf import settings

    by_user = {}
    for alert in alerts:
        uid = alert.rule.user_id
        by_user.setdefault(uid, {'user': alert.rule.user, 'alerts': []})
        by_user[uid]['alerts'].append(alert)

    for uid, bundle in by_user.items():
        email_alerts = [
            a for a in bundle['alerts']
            if 'email' in (a.rule.notification_channels or [])
        ]
        if email_alerts:
            send_mail(
                subject=f'Nile Intelligence: {len(email_alerts)} new alerts',
                message='\n'.join(f'• {a.title}: {a.message}' for a in email_alerts[:10]),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bundle['user'].email],
                fail_silently=True,
            )


@shared_task
def detect_market_events():
    """Detect significant market-wide events."""
    from apps.market.services import MarketAnalyticsService
    from .models import MarketEvent
    from django.utils import timezone

    rankings = MarketAnalyticsService.get_developer_rankings(20)
    # New project launches = compounds with first listing in last 24h
    from apps.properties.models import Compound, PropertyListing
    from django.db.models import Min

    new_compounds = Compound.objects.filter(
        listings__scraped_at__gte=timezone.now() - timezone.timedelta(hours=24)
    ).annotate(first_listing=Min('listings__scraped_at')).filter(
        first_listing__gte=timezone.now() - timezone.timedelta(hours=24)
    ).distinct()

    for compound in new_compounds:
        if not MarketEvent.objects.filter(
            event_type=MarketEvent.EventType.NEW_PROJECT_LAUNCH,
            metadata__compound_id=compound.id,
        ).exists():
            MarketEvent.objects.create(
                event_type=MarketEvent.EventType.NEW_PROJECT_LAUNCH,
                title=f'New project detected: {compound.name}',
                description=f'{compound.developer.name if compound.developer else "Unknown"} has launched a new project in {compound.area.name if compound.area else "Unknown area"}.',
                area=compound.area,
                developer=compound.developer,
                impact_score=7,
                metadata={'compound_id': compound.id, 'compound_slug': compound.slug},
            )
