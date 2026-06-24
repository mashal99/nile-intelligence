import scrapy


class PropertyItem(scrapy.Item):
    # Source
    source_url = scrapy.Field()
    source_id = scrapy.Field()
    source_portal = scrapy.Field()

    # Classification
    property_type = scrapy.Field()  # apartment, villa, etc.
    purpose = scrapy.Field()         # sale, rent, new_launch

    # Location
    area_name = scrapy.Field()
    compound_name = scrapy.Field()
    developer_name = scrapy.Field()

    # Details
    title = scrapy.Field()
    description = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    area_sqm = scrapy.Field()
    floor = scrapy.Field()
    total_floors = scrapy.Field()
    finishing = scrapy.Field()

    # Pricing
    price = scrapy.Field()
    down_payment = scrapy.Field()
    monthly_installment = scrapy.Field()
    installment_years = scrapy.Field()

    # Media
    images = scrapy.Field()

    # Meta
    listed_at = scrapy.Field()
    scraped_at = scrapy.Field()
