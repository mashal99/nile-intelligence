from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MonitoringRule, Alert, CompetitorWatch, MarketEvent
from . import serializers as s
from core.permissions import SubscriptionRequired


class MonitoringRuleListCreateView(generics.ListCreateAPIView):
    serializer_class = s.MonitoringRuleSerializer

    def get_queryset(self):
        return MonitoringRule.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MonitoringRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = s.MonitoringRuleSerializer

    def get_queryset(self):
        return MonitoringRule.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


class AlertListView(generics.ListAPIView):
    serializer_class = s.AlertSerializer

    def get_queryset(self):
        qs = Alert.objects.filter(rule__user=self.request.user).order_by('-created_at')
        unread_only = self.request.query_params.get('unread')
        if unread_only == 'true':
            qs = qs.filter(is_read=False)
        return qs


class AlertMarkReadView(APIView):
    def patch(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk, rule__user=request.user)
            alert.is_read = True
            alert.save(update_fields=['is_read'])
            return Response({'detail': 'Marked as read.'})
        except Alert.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AlertMarkAllReadView(APIView):
    def post(self, request):
        Alert.objects.filter(rule__user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'All alerts marked as read.'})


class CompetitorWatchListView(generics.ListCreateAPIView):
    serializer_class = s.CompetitorWatchSerializer

    def get_queryset(self):
        return CompetitorWatch.objects.filter(user=self.request.user).select_related('developer')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MarketEventListView(generics.ListAPIView):
    serializer_class = s.MarketEventSerializer
    queryset = MarketEvent.objects.select_related('area', 'developer').order_by('-detected_at')[:50]
