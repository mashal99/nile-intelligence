import re
import os
import sys
import django
from decimal import Decimal, InvalidOperation
from datetime import datetime

# Bootstrap Django for DB access from Scrapy
sys.path.insert(0, '/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()


class CleaningPipeline:
    """Normalize and validate scraped data before persistence."""

    PROPERTY_TYPE_MAP = {
        'شقة': 'apartment', 'apartment': 'apartment', 'flat': 'apartment',
        'فيلا': 'villa', 'villa': 'villa',
        'تاون هاوس': 'townhouse', 'townhouse': 'townhouse',
        'دوبلكس': 'duplex', 'duplex': 'duplex',
        'بنت هاوس': 'penthouse', 'penthouse': 'penthouse',
        'استوديو': 'studio', 'studio': 'studio',
        'شاليه': 'chalet', 'chalet': 'chalet',
        'توين هاوس': 'twin_house', 'twin house': 'twin_house',
    }

    def process_item(self, item, spider):
        # Normalize property type
        raw_type = str(item.get('property_type', '')).lower().strip()
        item['property_type'] = self.PROPERTY_TYPE_MAP.get(raw_type, 'apartment')

        # Normalize purpose
        raw_purpose = str(item.get('purpose', 'sale')).lower()
        item['purpose'] = 'rent' if 'rent' in raw_purpose or 'إيجار' in raw_purpose else 'sale'

        # Clean price
        item['price'] = self._clean_price(item.get('price'))
        item['down_payment'] = self._clean_price(item.get('down_payment'))
        item['monthly_installment'] = self._clean_price(item.get('monthly_installment'))

        # Clean numeric fields
        item['bedrooms'] = self._to_int(item.get('bedrooms'))
        item['bathrooms'] = self._to_int(item.get('bathrooms'))
        item['area_sqm'] = self._to_decimal(item.get('area_sqm'))
        item['floor'] = self._to_int(item.get('floor'))
        item['total_floors'] = self._to_int(item.get('total_floors'))
        item['installment_years'] = self._to_int(item.get('installment_years'))

        # Ensure images is a list
        images = item.get('images', [])
        item['images'] = list(images) if images else []

        # Truncate title
        if item.get('title'):
            item['title'] = str(item['title'])[:500]

        item['scraped_at'] = datetime.utcnow().isoformat()
        return item

    def _clean_price(self, value) -> Decimal | None:
        if not value:
            return None
        cleaned = re.sub(r'[^\d.]', '', str(value))
        if not cleaned:
            return None
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None

    def _to_int(self, value) -> int | None:
        if value is None:
            return None
        try:
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None

    def _to_decimal(self, value) -> Decimal | None:
        if value is None:
            return None
        try:
            cleaned = re.sub(r'[^\d.]', '', str(value))
            return Decimal(cleaned) if cleaned else None
        except (InvalidOperation, TypeError):
            return None


class DjangoPersistencePipeline:
    """Write cleaned items to Django/PostgreSQL."""

    def process_item(self, item, spider):
        from apps.properties.services import ListingIngestionService
        from apps.properties.models import ScrapingJob

        try:
            listing, created = ListingIngestionService.ingest(dict(item), item.get('source_portal', 'unknown'))

            # Update job counters
            job_id = getattr(spider, 'job_id', None)
            if job_id:
                if created:
                    ScrapingJob.objects.filter(pk=job_id).update(
                        listings_scraped=ScrapingJob.objects.get(pk=job_id).listings_scraped + 1,
                        listings_new=ScrapingJob.objects.get(pk=job_id).listings_new + 1,
                    )
                else:
                    ScrapingJob.objects.filter(pk=job_id).update(
                        listings_scraped=ScrapingJob.objects.get(pk=job_id).listings_scraped + 1,
                        listings_updated=ScrapingJob.objects.get(pk=job_id).listings_updated + 1,
                    )
        except Exception as e:
            spider.logger.error(f'Failed to persist item: {e} | URL: {item.get("source_url")}')

            job_id = getattr(spider, 'job_id', None)
            if job_id:
                ScrapingJob.objects.filter(pk=job_id).update(
                    listings_failed=ScrapingJob.objects.get(pk=job_id).listings_failed + 1,
                )

        return item


class DuplicateFilterPipeline:
    """In-memory URL dedup within a single spider run."""

    def open_spider(self, spider):
        self.seen_urls = set()

    def process_item(self, item, spider):
        url = item.get('source_url')
        if url in self.seen_urls:
            from scrapy.exceptions import DropItem
            raise DropItem(f'Duplicate URL: {url}')
        self.seen_urls.add(url)
        return item
