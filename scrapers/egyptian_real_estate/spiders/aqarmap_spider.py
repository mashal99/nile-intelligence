import re
from .base_spider import BaseEgyptianRealEstateSpider
from egyptian_real_estate.items import PropertyItem


class AqarmapSpider(BaseEgyptianRealEstateSpider):
    name = 'aqarmap'
    allowed_domains = ['aqarmap.com']
    portal = 'aqarmap'

    start_urls = [
        'https://aqarmap.com.eg/en/for-sale/property-type/cairo/',
        'https://aqarmap.com.eg/en/for-sale/property-type/giza/',
        'https://aqarmap.com.eg/en/for-sale/property-type/new-cairo/',
        'https://aqarmap.com.eg/en/for-sale/property-type/sheikh-zayed/',
        'https://aqarmap.com.eg/en/for-sale/property-type/new-administrative-capital/',
        'https://aqarmap.com.eg/en/for-sale/property-type/north-coast/',
        'https://aqarmap.com.eg/en/for-rent/property-type/cairo/',
        'https://aqarmap.com.eg/en/for-rent/property-type/giza/',
    ]

    @property
    def requires_playwright(self) -> bool:
        return True

    def extract_listing_urls(self, response) -> list[str]:
        return response.css('a.listing-card__link::attr(href)').getall()

    def extract_next_page(self, response) -> str | None:
        next_url = response.css('a[rel="next"]::attr(href)').get()
        if next_url:
            return response.urljoin(next_url)
        return None

    def parse_listing(self, response) -> PropertyItem:
        item = PropertyItem()
        item['source_url'] = response.url
        item['source_portal'] = self.portal
        item['source_id'] = re.search(r'/(\d+)/?$', response.url).group(1) if re.search(r'/(\d+)/?$', response.url) else ''

        # Purpose from URL
        item['purpose'] = 'rent' if '/for-rent/' in response.url else 'sale'

        # Property type
        breadcrumbs = response.css('.breadcrumb__item::text').getall()
        item['property_type'] = self._extract_property_type(breadcrumbs)

        item['title'] = self._safe_first(response.css('h1.listing-title::text'))
        item['description'] = self._safe_text(response.css('.listing-description p::text'))

        # Location
        item['area_name'] = self._safe_first(response.css('[data-testid="listing-location-area"]::text'))
        item['compound_name'] = self._safe_first(response.css('[data-testid="listing-compound-name"]::text'))
        item['developer_name'] = self._safe_first(response.css('[data-testid="listing-developer"]::text'))

        # Specs
        specs = {
            s.css('span.spec-label::text').get('').strip().lower():
            s.css('span.spec-value::text').get('').strip()
            for s in response.css('.listing-spec')
        }
        item['bedrooms'] = specs.get('bedrooms') or specs.get('غرف نوم')
        item['bathrooms'] = specs.get('bathrooms') or specs.get('حمامات')
        item['area_sqm'] = re.sub(r'[^\d.]', '', specs.get('area', '') or specs.get('المساحة', '')) or None
        item['floor'] = specs.get('floor') or specs.get('الدور')
        item['finishing'] = specs.get('finishing') or specs.get('التشطيب')

        # Price
        price_text = response.css('[data-testid="listing-price"]::text').get('')
        item['price'] = re.sub(r'[^\d]', '', price_text) or None

        down_text = response.css('[data-testid="down-payment"]::text').get('')
        item['down_payment'] = re.sub(r'[^\d]', '', down_text) or None

        installment_text = response.css('[data-testid="monthly-installment"]::text').get('')
        item['monthly_installment'] = re.sub(r'[^\d]', '', installment_text) or None

        years_text = response.css('[data-testid="installment-years"]::text').get('')
        year_match = re.search(r'(\d+)', years_text)
        item['installment_years'] = year_match.group(1) if year_match else None

        # Images
        item['images'] = response.css('.listing-gallery__image::attr(src)').getall()

        return item

    def _extract_property_type(self, breadcrumbs: list) -> str:
        type_map = {
            'apartments': 'apartment', 'villas': 'villa', 'townhouses': 'townhouse',
            'studios': 'studio', 'duplexes': 'duplex', 'chalets': 'chalet',
            'twin houses': 'twin_house', 'penthouses': 'penthouse',
        }
        for crumb in breadcrumbs:
            crumb_lower = crumb.strip().lower()
            for key, val in type_map.items():
                if key in crumb_lower:
                    return val
        return 'apartment'
