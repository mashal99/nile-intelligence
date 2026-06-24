from django.db import models
from django.conf import settings


class MonitoringRule(models.Model):
    """User-defined rules for competitor/market monitoring."""
    class RuleType(models.TextChoices):
        NEW_LISTING = 'new_listing', 'New Listing'
        PRICE_DROP = 'price_drop', 'Price Drop'
        PRICE_INCREASE = 'price_increase', 'Price Increase'
        SOLD_OUT = 'sold_out', 'Sold Out'
        NEW_LAUNCH = 'new_launch', 'New Launch'
        DEVELOPER_ACTIVITY = 'developer_activity', 'Developer Activity'

    class NotificationChannel(models.TextChoices):
        EMAIL = 'email', 'Email'
        IN_APP = 'in_app', 'In-App'
        WEBHOOK = 'webhook', 'Webhook'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monitoring_rules')
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=30, choices=RuleType.choices)

    # Scope filters
    area = models.ForeignKey('properties.Area', on_delete=models.SET_NULL, null=True, blank=True)
    developer = models.ForeignKey('properties.Developer', on_delete=models.SET_NULL, null=True, blank=True)
    compound = models.ForeignKey('properties.Compound', on_delete=models.SET_NULL, null=True, blank=True)
    property_type = models.CharField(max_length=20, blank=True)
    min_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Alert config
    price_change_threshold_pct = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    notification_channels = models.JSONField(default=list)
    webhook_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'monitoring_rules'
        indexes = [models.Index(fields=['user', 'is_active'])]


class Alert(models.Model):
    class AlertSeverity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    rule = models.ForeignKey(MonitoringRule, on_delete=models.CASCADE, related_name='alerts')
    listing = models.ForeignKey('properties.PropertyListing', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=500)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=AlertSeverity.choices, default=AlertSeverity.MEDIUM)
    metadata = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['rule', 'created_at']),
            models.Index(fields=['is_read']),
        ]


class CompetitorWatch(models.Model):
    """Track specific competitors (developers) for a user."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='competitor_watches')
    developer = models.ForeignKey('properties.Developer', on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'competitor_watches'
        unique_together = ['user', 'developer']


class MarketEvent(models.Model):
    """Significant market events detected by the system."""
    class EventType(models.TextChoices):
        NEW_PROJECT_LAUNCH = 'new_project_launch', 'New Project Launch'
        MASS_PRICE_CHANGE = 'mass_price_change', 'Mass Price Change'
        DEVELOPER_EXIT = 'developer_exit', 'Developer Exit'
        AREA_SURGE = 'area_surge', 'Area Surge'
        INVENTORY_SHORTAGE = 'inventory_shortage', 'Inventory Shortage'

    event_type = models.CharField(max_length=30, choices=EventType.choices)
    title = models.CharField(max_length=500)
    description = models.TextField()
    area = models.ForeignKey('properties.Area', on_delete=models.SET_NULL, null=True, blank=True)
    developer = models.ForeignKey('properties.Developer', on_delete=models.SET_NULL, null=True, blank=True)
    impact_score = models.PositiveSmallIntegerField(default=5)
    metadata = models.JSONField(default=dict)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'market_events'
        indexes = [models.Index(fields=['event_type', 'detected_at'])]
