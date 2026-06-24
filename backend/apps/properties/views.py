from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import PropertyListing, Developer, Area, Compound
from .serializers import (
    PropertyListingSerializer, PropertyListingDetailSerializer,
    DeveloperSerializer, DeveloperDetailSerializer,
    AreaSerializer, CompoundSerializer, PropertySearchSerializer,
    CompoundComparisonSerializer,
)
from .services import PropertySearchService


class PropertyListView(generics.ListAPIView):
    serializer_class = PropertyListingSerializer

    def get_queryset(self):
        s = PropertySearchSerializer(data=self.request.query_params)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        return PropertySearchService.search(
            query=d.get('q', ''),
            area_slug=d.get('area', ''),
            developer_slug=d.get('developer', ''),
            compound_slug=d.get('compound', ''),
            property_type=d.get('property_type', ''),
            min_price=d.get('min_price'),
            max_price=d.get('max_price'),
            min_bedrooms=d.get('min_bedrooms'),
            max_bedrooms=d.get('max_bedrooms'),
            purpose=d.get('purpose', ''),
            order_by=d.get('order_by', '-scraped_at'),
        )


class PropertyDetailView(generics.RetrieveAPIView):
    serializer_class = PropertyListingDetailSerializer
    queryset = PropertyListing.objects.select_related(
        'compound', 'compound__developer', 'developer', 'area'
    ).prefetch_related('price_history')


class DeveloperListView(generics.ListAPIView):
    serializer_class = DeveloperSerializer
    queryset = Developer.objects.filter(is_active=True).order_by('name')
    filterset_fields = []
    search_fields = ['name', 'name_ar']


class DeveloperDetailView(generics.RetrieveAPIView):
    serializer_class = DeveloperDetailSerializer
    queryset = Developer.objects.filter(is_active=True)
    lookup_field = 'slug'


class AreaListView(generics.ListAPIView):
    serializer_class = AreaSerializer
    queryset = Area.objects.filter(is_active=True, parent__isnull=True).order_by('name')
    search_fields = ['name', 'name_ar']


class CompoundListView(generics.ListAPIView):
    serializer_class = CompoundSerializer
    filterset_fields = ['developer__slug', 'area__slug']
    search_fields = ['name', 'name_ar']

    def get_queryset(self):
        return Compound.objects.filter(is_active=True).select_related('developer', 'area').order_by('name')


class CompoundDetailView(generics.RetrieveAPIView):
    serializer_class = CompoundSerializer
    queryset = Compound.objects.select_related('developer', 'area')
    lookup_field = 'slug'


class CompoundListingsView(generics.ListAPIView):
    serializer_class = PropertyListingSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return PropertyListing.objects.filter(
            compound__slug=slug,
            status=PropertyListing.ListingStatus.ACTIVE,
            canonical_listing__isnull=True,
        ).select_related('area', 'developer').order_by('-scraped_at')


class CompoundCompareView(APIView):
    def post(self, request):
        serializer = CompoundComparisonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        from apps.market.services import MarketAnalyticsService
        result = MarketAnalyticsService.compare_compounds(d['compound_slugs'], d['days'])
        return Response(result)
