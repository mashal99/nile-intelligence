from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status

from .models import Subscription, UsageRecord, Invoice
from . import serializers as s
from django.conf import settings


class CurrentSubscriptionView(APIView):
    def get(self, request):
        sub = request.user.subscriptions.filter(is_active=True).first()
        limits = settings.SUBSCRIPTION_PLANS.get(
            sub.plan if sub else 'free',
            settings.SUBSCRIPTION_PLANS['free']
        )
        return Response({
            'plan': sub.plan if sub else 'free',
            'billing_cycle': sub.billing_cycle if sub else None,
            'expires_at': sub.expires_at if sub else None,
            'auto_renew': sub.auto_renew if sub else False,
            'limits': limits,
        })


class UsageView(APIView):
    def get(self, request):
        from django.utils import timezone
        from datetime import date
        today = date.today()
        month_start = today.replace(day=1)

        records = UsageRecord.objects.filter(
            user=request.user,
            date__gte=month_start,
        ).values('usage_type').annotate(
            total=__import__('django.db.models', fromlist=['Sum']).Sum('count')
        )

        usage = {r['usage_type']: r['total'] for r in records}
        limits = settings.SUBSCRIPTION_PLANS.get(request.user.plan, settings.SUBSCRIPTION_PLANS['free'])

        return Response({'usage': usage, 'limits': limits})


class PlansView(APIView):
    permission_classes = []

    def get(self, request):
        return Response(settings.SUBSCRIPTION_PLANS)


class UpgradePlanView(APIView):
    def post(self, request):
        plan = request.data.get('plan')
        billing_cycle = request.data.get('billing_cycle', 'monthly')

        if plan not in settings.SUBSCRIPTION_PLANS:
            return Response({'detail': 'Invalid plan.'}, status=status.HTTP_400_BAD_REQUEST)

        # In production: integrate Stripe here
        # For now: directly upgrade (sandbox mode)
        sub, _ = Subscription.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={'plan': plan, 'billing_cycle': billing_cycle},
        )
        sub.plan = plan
        sub.billing_cycle = billing_cycle
        sub.save(update_fields=['plan', 'billing_cycle'])

        return Response({'detail': f'Upgraded to {plan}.', 'plan': plan})


class InvoiceListView(generics.ListAPIView):
    serializer_class = s.InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(
            subscription__user=self.request.user
        ).order_by('-issued_at')
