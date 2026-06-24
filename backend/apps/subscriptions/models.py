from django.db import models
from django.conf import settings


class Plan(models.TextChoices):
    FREE = 'free', 'Free'
    PROFESSIONAL = 'professional', 'Professional'
    ENTERPRISE = 'enterprise', 'Enterprise'


class BillingCycle(models.TextChoices):
    MONTHLY = 'monthly', 'Monthly'
    YEARLY = 'yearly', 'Yearly'


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    auto_renew = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'subscriptions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['plan']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.plan}'

    def get_limits(self):
        return settings.SUBSCRIPTION_PLANS.get(self.plan, settings.SUBSCRIPTION_PLANS['free'])


class UsageRecord(models.Model):
    class UsageType(models.TextChoices):
        API_CALL = 'api_call', 'API Call'
        REPORT_GENERATED = 'report_generated', 'Report Generated'
        AI_QUERY = 'ai_query', 'AI Query'
        LISTING_VIEW = 'listing_view', 'Listing View'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usage_records')
    usage_type = models.CharField(max_length=30, choices=UsageType.choices)
    count = models.PositiveIntegerField(default=1)
    date = models.DateField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'usage_records'
        unique_together = ['user', 'usage_type', 'date']
        indexes = [models.Index(fields=['user', 'date'])]


class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    invoice_pdf_url = models.URLField(blank=True)

    class Meta:
        db_table = 'invoices'
