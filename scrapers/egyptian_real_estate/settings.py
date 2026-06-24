BOT_NAME = 'egyptian_real_estate'
SPIDER_MODULES = ['egyptian_real_estate.spiders']
NEWSPIDER_MODULE = 'egyptian_real_estate.spiders'

# Respect robots.txt — disable for specific portals as needed
ROBOTSTXT_OBEY = False

# Rate limiting — be a good citizen
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

COOKIES_ENABLED = True
TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
}

# Playwright for JS-rendered pages
DOWNLOAD_HANDLERS = {
    'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
    'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
}
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
PLAYWRIGHT_BROWSER_TYPE = 'chromium'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,
    'args': ['--no-sandbox', '--disable-dev-shm-usage'],
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'egyptian_real_estate.middlewares.RotatingUserAgentMiddleware': 400,
    'egyptian_real_estate.middlewares.ProxyMiddleware': 350,
}

ITEM_PIPELINES = {
    'egyptian_real_estate.pipelines.DuplicateFilterPipeline': 100,
    'egyptian_real_estate.pipelines.CleaningPipeline': 200,
    'egyptian_real_estate.pipelines.DjangoPersistencePipeline': 300,
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

LOG_LEVEL = 'INFO'

HTTPCACHE_ENABLED = False
