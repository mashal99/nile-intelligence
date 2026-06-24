from datetime import date, timedelta
from django.db.models import Avg, Min, Max, Count, Q
from django.db import connection

from apps.properties.models import PropertyListing, Area, Developer, Compound
from .models import MarketSnapshot, CompoundSnapshot, DeveloperMetrics, MarketInsight


class MarketSnapshotService:
    """Computes and stores daily market aggregates. Called by Celery beat."""

    @staticmethod
    def compute_daily_snapshot(snapshot_date: date = None) -> int:
        if snapshot_date is None:
            snapshot_date = date.today()

        active_qs = PropertyListing.objects.filter(
            status=PropertyListing.ListingStatus.ACTIVE,
            canonical_listing__isnull=True,
        )

        areas = Area.objects.filter(listings__isnull=False).distinct()
        property_types = ['apartment', 'villa', 'townhouse', 'twin_house', 'studio', 'chalet']
        created = 0

        for area in areas:
            for ptype in property_types:
                qs = active_qs.filter(area=area, property_type=ptype, price__isnull=False)
                count = qs.count()
                if count == 0:
                    continue

                stats = qs.aggregate(
                    avg_price=Avg('price'),
                    min_price=Min('price'),
                    max_price=Max('price'),
                    avg_psm=Avg('price_per_sqm'),
                )

                prices = list(qs.values_list('price', flat=True).order_by('price'))
                mid = len(prices) // 2
                median_price = prices[mid] if len(prices) % 2 == 1 else (prices[mid - 1] + prices[mid]) / 2

                psms = list(qs.filter(price_per_sqm__isnull=False).values_list('price_per_sqm', flat=True).order_by('price_per_sqm'))
                mid_psm = len(psms) // 2
                median_psm = psms[mid_psm] if psms and len(psms) % 2 == 1 else (
                    (psms[mid_psm - 1] + psms[mid_psm]) / 2 if psms else None
                )

                new_listings = PropertyListing.objects.filter(
                    area=area,
                    property_type=ptype,
                    scraped_at__date=snapshot_date,
                ).count()

                snap, _ = MarketSnapshot.objects.update_or_create(
                    area=area,
                    property_type=ptype,
                    date=snapshot_date,
                    defaults={
                        'avg_price': stats['avg_price'] or 0,
                        'median_price': median_price,
                        'min_price': stats['min_price'] or 0,
                        'max_price': stats['max_price'] or 0,
                        'avg_price_per_sqm': stats['avg_psm'] or 0,
                        'median_price_per_sqm': median_psm or 0,
                        'active_listings': count,
                        'new_listings': new_listings,
                    }
                )

                MarketSnapshotService._compute_price_changes(snap, snapshot_date)
                created += 1

        return created

    @staticmethod
    def _compute_price_changes(snap: MarketSnapshot, today: date) -> None:
        def get_avg(days_ago: int):
            past_date = today - timedelta(days=days_ago)
            try:
                past = MarketSnapshot.objects.get(
                    area=snap.area,
                    property_type=snap.property_type,
                    date=past_date,
                )
                return past.avg_price
            except MarketSnapshot.DoesNotExist:
                return None

        changes = {}
        for days, field in [(7, 'price_change_7d'), (30, 'price_change_30d'), (90, 'price_change_90d')]:
            past_avg = get_avg(days)
            if past_avg and past_avg > 0:
                changes[field] = ((snap.avg_price - past_avg) / past_avg) * 100
            else:
                changes[field] = None

        MarketSnapshot.objects.filter(pk=snap.pk).update(**changes)

    @staticmethod
    def compute_compound_snapshots(snapshot_date: date = None) -> int:
        if snapshot_date is None:
            snapshot_date = date.today()

        compounds = Compound.objects.filter(listings__isnull=False).distinct()
        created = 0

        for compound in compounds:
            qs = PropertyListing.objects.filter(
                compound=compound,
                status=PropertyListing.ListingStatus.ACTIVE,
                canonical_listing__isnull=True,
                price__isnull=False,
            )
            if not qs.exists():
                continue

            stats = qs.aggregate(
                avg_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price'),
                avg_psm=Avg('price_per_sqm'),
                count=Count('id'),
            )

            CompoundSnapshot.objects.update_or_create(
                compound=compound,
                date=snapshot_date,
                defaults={
                    'avg_price': stats['avg_price'],
                    'avg_price_per_sqm': stats['avg_psm'],
                    'active_listings': stats['count'],
                    'min_price': stats['min_price'],
                    'max_price': stats['max_price'],
                }
            )
            created += 1

        return created


class MarketAnalyticsService:
    @staticmethod
    def get_price_trend(area_slug: str, property_type: str, days: int = 90) -> list[dict]:
        cutoff = date.today() - timedelta(days=days)
        snapshots = MarketSnapshot.objects.filter(
            area__slug=area_slug,
            property_type=property_type,
            date__gte=cutoff,
        ).order_by('date').values('date', 'avg_price', 'median_price', 'avg_price_per_sqm', 'active_listings')
        return list(snapshots)

    @staticmethod
    def get_area_heatmap() -> list[dict]:
        """Returns average price per sqm per area for the last available snapshot."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.name,
                    a.slug,
                    a.latitude,
                    a.longitude,
                    AVG(ms.avg_price_per_sqm) as avg_psm,
                    SUM(ms.active_listings) as total_listings
                FROM market_snapshots ms
                JOIN areas a ON a.id = ms.area_id
                WHERE ms.date = (SELECT MAX(date) FROM market_snapshots)
                GROUP BY a.id, a.name, a.slug, a.latitude, a.longitude
                ORDER BY avg_psm DESC
            """)
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_developer_rankings(limit: int = 20) -> list[dict]:
        return list(
            Developer.objects.filter(is_active=True)
            .annotate(
                active_count=Count('listings', filter=Q(listings__status='active')),
                avg_psm=Avg('listings__price_per_sqm', filter=Q(listings__status='active')),
            )
            .filter(active_count__gt=0)
            .order_by('-active_count')
            .values('name', 'slug', 'active_count', 'avg_psm', 'total_projects')[:limit]
        )

    @staticmethod
    def get_inventory_summary() -> dict:
        qs = PropertyListing.objects.filter(
            canonical_listing__isnull=True,
        )
        return {
            'total_active': qs.filter(status='active').count(),
            'new_last_7d': qs.filter(
                scraped_at__gte=date.today() - timedelta(days=7)
            ).count(),
            'by_type': list(
                qs.filter(status='active')
                .values('property_type')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
            'by_purpose': list(
                qs.filter(status='active')
                .values('purpose')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
        }

    @staticmethod
    def compare_compounds(compound_slugs: list[str], days: int = 30) -> list[dict]:
        cutoff = date.today() - timedelta(days=days)
        result = []
        for slug in compound_slugs:
            snaps = CompoundSnapshot.objects.filter(
                compound__slug=slug,
                date__gte=cutoff,
            ).order_by('date').values('date', 'avg_price', 'avg_price_per_sqm', 'active_listings')
            result.append({'compound': slug, 'data': list(snaps)})
        return result
