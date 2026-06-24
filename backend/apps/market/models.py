from django.db import models
from django.contrib.postgres.fields import ArrayField


class MarketSnapshot(models.Model):
    """Daily aggregate market data per area/type combination."""
    area = models.ForeignKey('properties.Area', on_delete=models.CASCADE, related_name='snapshots')
    property_type = models.CharField(max_length=20)
    date = models.DateField()

    # Pricing stats
    avg_price = models.DecimalField(max_digits=15, decimal_places=2)
    median_price = models.DecimalField(max_digits=15, decimal_places=2)
    min_price = models.DecimalField(max_digits=15, decimal_places=2)
    max_price = models.DecimalField(max_digits=15, decimal_places=2)
    avg_price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    median_price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2)

    # Volume
    active_listings = models.PositiveIntegerField(default=0)
    new_listings = models.PositiveIntegerField(default=0)
    sold_listings = models.PositiveIntegerField(default=0)
    removed_listings = models.PositiveIntegerField(default=0)

    # Price movement
    price_change_7d = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    price_change_30d = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    price_change_90d = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'market_snapshots'
        unique_together = ['area', 'property_type', 'date']
        indexes = [
            models.Index(fields=['area', 'date']),
            models.Index(fields=['date']),
        ]


class CompoundSnapshot(models.Model):
    """Daily compound-level stats."""
    compound = models.ForeignKey('properties.Compound', on_delete=models.CASCADE, related_name='snapshots')
    date = models.DateField()

    avg_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    avg_price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    active_listings = models.PositiveIntegerField(default=0)
    total_listings_seen = models.PositiveIntegerField(default=0)
    min_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    max_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    class Meta:
        db_table = 'compound_snapshots'
        unique_together = ['compound', 'date']
        indexes = [models.Index(fields=['compound', 'date'])]


class DeveloperMetrics(models.Model):
    """Weekly developer performance metrics."""
    developer = models.ForeignKey('properties.Developer', on_delete=models.CASCADE, related_name='metrics')
    week_start = models.DateField()

    active_listings = models.PositiveIntegerField(default=0)
    new_launches = models.PositiveIntegerField(default=0)
    avg_price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    compounds_active = models.PositiveIntegerField(default=0)
    price_change_pct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    market_share_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        db_table = 'developer_metrics'
        unique_together = ['developer', 'week_start']


class MarketInsight(models.Model):
    """AI-generated market insight summaries."""
    class InsightType(models.TextChoices):
        WEEKLY_SUMMARY = 'weekly_summary', 'Weekly Summary'
        AREA_ANALYSIS = 'area_analysis', 'Area Analysis'
        DEVELOPER_REPORT = 'developer_report', 'Developer Report'
        PRICE_MOVEMENT = 'price_movement', 'Price Movement'
        INVESTMENT_OPPORTUNITY = 'investment_opportunity', 'Investment Opportunity'

    insight_type = models.CharField(max_length=30, choices=InsightType.choices)
    title = models.CharField(max_length=500)
    summary = models.TextField()
    full_analysis = models.TextField()
    area = models.ForeignKey('properties.Area', on_delete=models.SET_NULL, null=True, blank=True)
    developer = models.ForeignKey('properties.Developer', on_delete=models.SET_NULL, null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    ai_model = models.CharField(max_length=50, default='claude-sonnet-4-6')
    tokens_used = models.PositiveIntegerField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'market_insights'
        indexes = [
            models.Index(fields=['insight_type', 'generated_at']),
            models.Index(fields=['area']),
        ]
