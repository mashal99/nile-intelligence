import scrapy
from abc import abstractmethod
from egyptian_real_estate.items import PropertyItem


class BaseEgyptianRealEstateSpider(scrapy.Spider):
    custom_settings = {
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 30000,
    }

    def __init__(self, job_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_id = int(job_id) if job_id else None

    def parse(self, response, **kwargs):
        """Parse listing index page, yield requests to detail pages."""
        for url in self.extract_listing_urls(response):
            yield scrapy.Request(
                url,
                callback=self.parse_listing,
                meta={'playwright': self.requires_playwright},
            )

        next_page = self.extract_next_page(response)
        if next_page:
            yield scrapy.Request(
                next_page,
                callback=self.parse,
                meta={'playwright': self.requires_playwright},
            )

    @abstractmethod
    def extract_listing_urls(self, response) -> list[str]:
        pass

    @abstractmethod
    def extract_next_page(self, response) -> str | None:
        pass

    @abstractmethod
    def parse_listing(self, response) -> PropertyItem:
        pass

    @property
    def requires_playwright(self) -> bool:
        return False

    def _safe_text(self, selector, default='') -> str:
        texts = selector.getall()
        return ' '.join(t.strip() for t in texts if t.strip()) or default

    def _safe_first(self, selector, default=None):
        result = selector.get()
        return result.strip() if result else default
