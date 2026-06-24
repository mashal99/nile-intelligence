import re
import json
from .base_spider import BaseEgyptianRealEstateSpider
from egyptian_real_estate.items import PropertyItem


class NawySpider(BaseEgyptianRealEstateSpider):
    """
    Nawy.com — new developments portal. Uses their JSON API where possible.
    """
    name = 'nawy'
    allowed_domains = ['nawy.com']
    portal = 'nawy'

    API_BASE = 'https://api.nawy.com/api/v2'

    start_urls = [
        f'{API_BASE}/properties?city=cairo&page=1&per_page=50',
        f'{API_BASE}/properties?city=new-cairo&page=1&per_page=50',
        f'{API_BASE}/properties?city=sheikh-zayed&page=1&per_page=50',
        f'{API_BASE}/properties?city=north-coast&page=1&per_page=50',
        f'{API_BASE}/properties?city=new-capital&page=1&per_page=50',
    ]

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    }

    def parse(self, response, **kwargs):
        try:
            data = response.json()
        except Exception:
            self.logger.error(f'Failed to parse JSON from {response.url}')
            return

        properties = data.get('data', data.get('properties', []))
        for prop in properties:
            yield self._map_property(prop, response.url)

        meta = data.get('meta', {})
        current_page = meta.get('current_page', 1)
        last_page = meta.get('last_page', 1)
        if current_page < last_page:
            next_url = re.sub(r'page=\d+', f'page={current_page + 1}', response.url)
            yield response.follow(next_url, callback=self.parse)

    def extract_listing_urls(self, response): return []
    def extract_next_page(self, response): return None
    def parse_listing(self, response): return PropertyItem()

    def _map_property(self, prop: dict, source_url: str) -> PropertyItem:
        item = PropertyItem()
        prop_id = prop.get('id', '')
        item['source_url'] = f'https://nawy.com/properties/{prop_id}'
        item['source_id'] = str(prop_id)
        item['source_portal'] = self.portal
        item['purpose'] = 'sale'

        item['title'] = prop.get('name', '') or prop.get('title', '')
        item['description'] = prop.get('description', '')

        item['property_type'] = self._map_type(prop.get('property_type', ''))

        location = prop.get('location', {})
        item['area_name'] = location.get('area', {}).get('name', '') or prop.get('area_name', '')
        item['compound_name'] = prop.get('compound', {}).get('name', '') or prop.get('compound_name', '')
        item['developer_name'] = prop.get('developer', {}).get('name', '') or prop.get('developer_name', '')

        item['bedrooms'] = prop.get('bedrooms')
        item['bathrooms'] = prop.get('bathrooms')
        item['area_sqm'] = prop.get('area') or prop.get('area_sqm')
        item['floor'] = prop.get('floor')
        item['finishing'] = prop.get('finishing_type', '')

        item['price'] = prop.get('price') or prop.get('min_price')
        item['down_payment'] = prop.get('down_payment') or prop.get('min_down_payment')
        item['monthly_installment'] = prop.get('monthly_installment')
        item['installment_years'] = prop.get('payment_years') or prop.get('installment_years')

        images_raw = prop.get('images', [])
        item['images'] = [
            img.get('url', img) if isinstance(img, dict) else img
            for img in images_raw
        ]

        return item

    def _map_type(self, raw: str) -> str:
        mapping = {
            'apartment': 'apartment', 'villa': 'villa', 'townhouse': 'townhouse',
            'twin house': 'twin_house', 'duplex': 'duplex', 'penthouse': 'penthouse',
            'studio': 'studio', 'chalet': 'chalet',
        }
        return mapping.get(raw.lower().strip(), 'apartment')
