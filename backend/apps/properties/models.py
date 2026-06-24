from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class Developer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    name_ar = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='developers/', null=True, blank=True)
    website = models.URLField(blank=True)
    founded_year = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    total_projects = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'developers'
        indexes = [models.Index(fields=['slug']), models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='sub_areas')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'areas'
        indexes = [models.Index(fields=['slug']), models.Index(fields=['parent'])]

    def __str__(self):
        return self.name


class Compound(models.Model):
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True, related_name='compounds')
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, related_name='compounds')
    description = models.TextField(blank=True)
    launch_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    total_units = models.PositiveIntegerField(null=True, blank=True)
    land_area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    amenities = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    images = ArrayField(models.URLField(), default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compounds'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['developer']),
            models.Index(fields=['area']),
        ]

    def __str__(self):
        return f'{self.name} - {self.developer}'


class PropertyListing(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = 'apartment', 'Apartment'
        VILLA = 'villa', 'Villa'
        TOWNHOUSE = 'townhouse', 'Townhouse'
        TWIN_HOUSE = 'twin_house', 'Twin House'
        DUPLEX = 'duplex', 'Duplex'
        PENTHOUSE = 'penthouse', 'Penthouse'
        STUDIO = 'studio', 'Studio'
        OFFICE = 'office', 'Office'
        RETAIL = 'retail', 'Retail'
        CHALET = 'chalet', 'Chalet'

    class ListingStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SOLD = 'sold', 'Sold'
        RENTED = 'rented', 'Rented'
        UNAVAILABLE = 'unavailable', 'Unavailable'
        PRICE_CHANGED = 'price_changed', 'Price Changed'

    class PurposeType(models.TextChoices):
        SALE = 'sale', 'For Sale'
        RENT = 'rent', 'For Rent'
        NEW_LAUNCH = 'new_launch', 'New Launch'

    class FinishingType(models.TextChoices):
        CORE_SHELL = 'core_shell', 'Core & Shell'
        SEMI_FINISHED = 'semi_finished', 'Semi Finished'
        FULLY_FINISHED = 'fully_finished', 'Fully Finished'
        SUPER_LUX = 'super_lux', 'Super Lux'
        FURNISHED = 'furnished', 'Furnished'

    # Source tracking
    source_url = models.URLField(max_length=1000, unique=True)
    source_id = models.CharField(max_length=255, blank=True)
    source_portal = models.CharField(max_length=50)

    # Relations
    compound = models.ForeignKey(Compound, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')

    # Classification
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    purpose = models.CharField(max_length=20, choices=PurposeType.choices, default=PurposeType.SALE)
    status = models.CharField(max_length=20, choices=ListingStatus.choices, default=ListingStatus.ACTIVE)
    finishing = models.CharField(max_length=20, choices=FinishingType.choices, blank=True)

    # Specs
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    floor = models.PositiveSmallIntegerField(null=True, blank=True)
    total_floors = models.PositiveSmallIntegerField(null=True, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    down_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installment_years = models.PositiveSmallIntegerField(null=True, blank=True)

    # Media
    images = ArrayField(models.URLField(), default=list, blank=True)

    # Search
    search_vector = SearchVectorField(null=True, blank=True)

    # Timestamps
    listed_at = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked_at = models.DateTimeField(auto_now=True)

    # Deduplication
    fingerprint = models.CharField(max_length=64, blank=True, db_index=True)
    canonical_listing = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='duplicates'
    )

    class Meta:
        db_table = 'property_listings'
        indexes = [
            models.Index(fields=['source_portal', 'source_id']),
            models.Index(fields=['compound', 'status']),
            models.Index(fields=['area', 'property_type']),
            models.Index(fields=['price']),
            models.Index(fields=['price_per_sqm']),
            models.Index(fields=['bedrooms']),
            models.Index(fields=['scraped_at']),
            models.Index(fields=['status']),
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return f'{self.title} - {self.price} EGP'

    def save(self, *args, **kwargs):
        if self.price and self.area_sqm and self.area_sqm > 0:
            self.price_per_sqm = self.price / self.area_sqm
        super().save(*args, **kwargs)


class ListingPriceHistory(models.Model):
    listing = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=15, decimal_places=2)
    new_price = models.DecimalField(max_digits=15, decimal_places=2)
    change_percent = models.DecimalField(max_digits=6, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listing_price_history'
        indexes = [models.Index(fields=['listing', 'recorded_at'])]


class ListingStatusHistory(models.Model):
    listing = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listing_status_history'


class ScrapingJob(models.Model):
    class JobStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        PARTIAL = 'partial', 'Partial'

    portal = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.PENDING)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    listings_scraped = models.PositiveIntegerField(default=0)
    listings_new = models.PositiveIntegerField(default=0)
    listings_updated = models.PositiveIntegerField(default=0)
    listings_failed = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'scraping_jobs'
        indexes = [models.Index(fields=['portal', 'started_at'])]
