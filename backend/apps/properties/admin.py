from django.contrib import admin
from .models import Developer, Area, Compound, PropertyListing, ListingPriceHistory, ScrapingJob


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'total_projects', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_ar']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'name_ar']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Compound)
class CompoundAdmin(admin.ModelAdmin):
    list_display = ['name', 'developer', 'area', 'launch_date', 'is_active']
    list_filter = ['is_active', 'area']
    search_fields = ['name', 'developer__name']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['developer', 'area']


@admin.register(PropertyListing)
class PropertyListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'purpose', 'status', 'price', 'area', 'source_portal', 'scraped_at']
    list_filter = ['property_type', 'purpose', 'status', 'source_portal']
    search_fields = ['title', 'compound__name', 'developer__name']
    raw_id_fields = ['compound', 'developer', 'area', 'canonical_listing']
    readonly_fields = ['fingerprint', 'scraped_at', 'updated_at', 'price_per_sqm']


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ['portal', 'status', 'listings_scraped', 'listings_new', 'listings_failed', 'started_at']
    list_filter = ['portal', 'status']
    readonly_fields = ['started_at', 'celery_task_id']
