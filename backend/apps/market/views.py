from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, serializers as drf_serializers

from .models import MarketSnapshot, MarketInsight
from .services import MarketAnalyticsService


class PriceTrendView(APIView):
    def get(self, request, area_slug):
        property_type = request.query_params.get('type', 'apartment')
        days = int(request.query_params.get('days', 90))
        days = min(max(days, 7), 365)
        data = MarketAnalyticsService.get_price_trend(area_slug, property_type, days)
        return Response(data)


class AreaHeatmapView(APIView):
    def get(self, request):
        data = MarketAnalyticsService.get_area_heatmap()
        return Response(data)


class DeveloperRankingsView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        data = MarketAnalyticsService.get_developer_rankings(min(limit, 50))
        return Response(data)


class InventorySummaryView(APIView):
    def get(self, request):
        data = MarketAnalyticsService.get_inventory_summary()
        return Response(data)


class MarketInsightListView(generics.ListAPIView):
    class MarketInsightSerializer(drf_serializers.ModelSerializer):
        area_name = drf_serializers.CharField(source='area.name', read_only=True, allow_null=True)

        class Meta:
            model = MarketInsight
            fields = [
                'id', 'insight_type', 'title', 'summary', 'area_name',
                'tags', 'generated_at', 'valid_until',
            ]

    serializer_class = MarketInsightSerializer

    def get_queryset(self):
        qs = MarketInsight.objects.order_by('-generated_at')
        insight_type = self.request.query_params.get('type')
        if insight_type:
            qs = qs.filter(insight_type=insight_type)
        return qs[:50]


class MarketInsightDetailView(generics.RetrieveAPIView):
    class MarketInsightDetailSerializer(drf_serializers.ModelSerializer):
        class Meta:
            model = MarketInsight
            fields = '__all__'

    serializer_class = MarketInsightDetailSerializer
    queryset = MarketInsight.objects.all()


class DashboardSummaryView(APIView):
    """Single endpoint that powers the main dashboard."""

    def get(self, request):
        inventory = MarketAnalyticsService.get_inventory_summary()
        rankings = MarketAnalyticsService.get_developer_rankings(5)
        heatmap = MarketAnalyticsService.get_area_heatmap()

        # Latest insights
        insights = list(
            MarketInsight.objects.order_by('-generated_at').values(
                'id', 'insight_type', 'title', 'summary', 'generated_at'
            )[:3]
        )

        return Response({
            'inventory': inventory,
            'top_developers': rankings,
            'area_heatmap': heatmap[:10],
            'latest_insights': insights,
        })
