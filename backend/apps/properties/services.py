import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import PropertyListing, ListingPriceHistory, ListingStatusHistory, Compound, Developer, Area


def _compute_fingerprint(data: dict) -> str:
    """Stable fingerprint for deduplication across portals."""
    key_fields = {
        'compound': data.get('compound_name', '').lower().strip(),
        'bedrooms': data.get('bedrooms'),
        'area_sqm': str(data.get('area_sqm', '')),
        'floor': data.get('floor'),
        'property_type': data.get('property_type', ''),
    }
    payload = json.dumps(key_fields, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


class ListingIngestionService:
    """Handles raw scraped data → normalized DB records."""

    @staticmethod
    @transaction.atomic
    def ingest(raw: dict, portal: str) -> tuple[PropertyListing, bool]:
        """
        Returns (listing, created). Handles dedup, price tracking, status tracking.
        """
        source_url = raw.get('source_url')
        if not source_url:
            raise ValueError('source_url is required')

        # Resolve FK relations
        area = ListingIngestionService._resolve_area(raw.get('area_name'))
        developer = ListingIngestionService._resolve_developer(raw.get('developer_name'))
        compound = ListingIngestionService._resolve_compound(
            raw.get('compound_name'), developer=developer, area=area
        )

        fingerprint = _compute_fingerprint(raw)

        try:
            listing = PropertyListing.objects.get(source_url=source_url)
            created = False
            ListingIngestionService._check_and_record_changes(listing, raw)
        except PropertyListing.DoesNotExist:
            # Check fingerprint dedup across portals
            canonical = PropertyListing.objects.filter(
                fingerprint=fingerprint,
                canonical_listing__isnull=True,
            ).exclude(source_url=source_url).first()

            listing = PropertyListing(source_url=source_url, fingerprint=fingerprint)
            if canonical:
                listing.canonical_listing = canonical
            created = True

        # Map all fields
        listing.source_id = raw.get('source_id', '')
        listing.source_portal = portal
        listing.compound = compound
        listing.developer = developer
        listing.area = area
        listing.property_type = raw.get('property_type', '')
        listing.purpose = raw.get('purpose', 'sale')
        listing.finishing = raw.get('finishing', '')
        listing.title = raw.get('title', '')[:500]
        listing.description = raw.get('description', '')
        listing.bedrooms = raw.get('bedrooms')
        listing.bathrooms = raw.get('bathrooms')
        listing.area_sqm = raw.get('area_sqm')
        listing.floor = raw.get('floor')
        listing.total_floors = raw.get('total_floors')
        listing.price = raw.get('price')
        listing.down_payment = raw.get('down_payment')
        listing.monthly_installment = raw.get('monthly_installment')
        listing.installment_years = raw.get('installment_years')
        listing.images = raw.get('images', [])
        listing.status = PropertyListing.ListingStatus.ACTIVE
        listing.save()
        return listing, created

    @staticmethod
    def _check_and_record_changes(listing: PropertyListing, raw: dict) -> None:
        new_price = raw.get('price')
        if new_price and listing.price and Decimal(str(new_price)) != listing.price:
            change = (Decimal(str(new_price)) - listing.price) / listing.price * 100
            ListingPriceHistory.objects.create(
                listing=listing,
                old_price=listing.price,
                new_price=new_price,
                change_percent=change,
            )
            listing.status = PropertyListing.ListingStatus.PRICE_CHANGED

    @staticmethod
    def _resolve_area(name: str) -> Area | None:
        if not name:
            return None
        from django.utils.text import slugify
        slug = slugify(name)
        area, _ = Area.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'name_ar': ''},
        )
        return area

    @staticmethod
    def _resolve_developer(name: str) -> Developer | None:
        if not name:
            return None
        from django.utils.text import slugify
        slug = slugify(name)
        dev, _ = Developer.objects.get_or_create(
            slug=slug,
            defaults={'name': name},
        )
        return dev

    @staticmethod
    def _resolve_compound(name: str, developer=None, area=None) -> Compound | None:
        if not name:
            return None
        from django.utils.text import slugify
        slug = slugify(name)
        compound, created = Compound.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'developer': developer, 'area': area},
        )
        if created and developer:
            Developer.objects.filter(pk=developer.pk).update(
                total_projects=models_F('total_projects') + 1
            )
        return compound

    @staticmethod
    def mark_unavailable(source_url: str) -> None:
        try:
            listing = PropertyListing.objects.get(source_url=source_url)
            if listing.status == PropertyListing.ListingStatus.ACTIVE:
                ListingStatusHistory.objects.create(
                    listing=listing,
                    old_status=listing.status,
                    new_status=PropertyListing.ListingStatus.UNAVAILABLE,
                )
                listing.status = PropertyListing.ListingStatus.UNAVAILABLE
                listing.save(update_fields=['status', 'updated_at'])
        except PropertyListing.DoesNotExist:
            pass


# Import needed
from django.db.models import F as models_F


class PropertySearchService:
    @staticmethod
    def search(
        query: str = '',
        area_slug: str = '',
        developer_slug: str = '',
        compound_slug: str = '',
        property_type: str = '',
        min_price: float = None,
        max_price: float = None,
        min_bedrooms: int = None,
        max_bedrooms: int = None,
        purpose: str = '',
        order_by: str = '-scraped_at',
    ):
        qs = PropertyListing.objects.filter(
            status=PropertyListing.ListingStatus.ACTIVE,
            canonical_listing__isnull=True,
        ).select_related('compound', 'developer', 'area')

        if query:
            from django.contrib.postgres.search import SearchQuery, SearchRank
            search_query = SearchQuery(query)
            qs = qs.filter(search_vector=search_query).annotate(
                rank=SearchRank('search_vector', search_query)
            ).order_by('-rank')

        if area_slug:
            qs = qs.filter(area__slug=area_slug)
        if developer_slug:
            qs = qs.filter(developer__slug=developer_slug)
        if compound_slug:
            qs = qs.filter(compound__slug=compound_slug)
        if property_type:
            qs = qs.filter(property_type=property_type)
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        if min_bedrooms is not None:
            qs = qs.filter(bedrooms__gte=min_bedrooms)
        if max_bedrooms is not None:
            qs = qs.filter(bedrooms__lte=max_bedrooms)
        if purpose:
            qs = qs.filter(purpose=purpose)

        if not query:
            qs = qs.order_by(order_by)

        return qs
