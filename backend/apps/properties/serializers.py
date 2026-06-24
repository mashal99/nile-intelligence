from rest_framework import serializers
from .models import PropertyListing, Compound, Developer, Area, ListingPriceHistory


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name', 'slug', 'parent']


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ['id', 'name', 'slug', 'logo', 'website', 'total_projects', 'founded_year']


class DeveloperDetailSerializer(DeveloperSerializer):
    active_listings = serializers.SerializerMethodField()
    avg_price_per_sqm = serializers.SerializerMethodField()

    class Meta(DeveloperSerializer.Meta):
        fields = DeveloperSerializer.Meta.fields + ['description', 'active_listings', 'avg_price_per_sqm']

    def get_active_listings(self, obj):
        return obj.listings.filter(status='active').count()

    def get_avg_price_per_sqm(self, obj):
        from django.db.models import Avg
        result = obj.listings.filter(status='active', price_per_sqm__isnull=False).aggregate(Avg('price_per_sqm'))
        return result['price_per_sqm__avg']


class CompoundSerializer(serializers.ModelSerializer):
    developer = DeveloperSerializer(read_only=True)
    area = AreaSerializer(read_only=True)

    class Meta:
        model = Compound
        fields = [
            'id', 'name', 'slug', 'developer', 'area', 'launch_date',
            'delivery_date', 'total_units', 'land_area', 'amenities',
            'images', 'latitude', 'longitude',
        ]


class ListingPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPriceHistory
        fields = ['old_price', 'new_price', 'change_percent', 'recorded_at']


class PropertyListingSerializer(serializers.ModelSerializer):
    area = AreaSerializer(read_only=True)
    developer = DeveloperSerializer(read_only=True)
    compound_name = serializers.CharField(source='compound.name', read_only=True, allow_null=True)

    class Meta:
        model = PropertyListing
        fields = [
            'id', 'title', 'property_type', 'purpose', 'status', 'finishing',
            'bedrooms', 'bathrooms', 'area_sqm', 'floor', 'total_floors',
            'price', 'price_per_sqm', 'down_payment', 'monthly_installment',
            'installment_years', 'area', 'developer', 'compound_name',
            'source_url', 'source_portal', 'images', 'scraped_at', 'updated_at',
        ]


class PropertyListingDetailSerializer(PropertyListingSerializer):
    compound = CompoundSerializer(read_only=True)
    price_history = ListingPriceHistorySerializer(many=True, read_only=True)

    class Meta(PropertyListingSerializer.Meta):
        fields = PropertyListingSerializer.Meta.fields + [
            'compound', 'description', 'price_history', 'listed_at',
        ]


class CompoundComparisonSerializer(serializers.Serializer):
    compound_slugs = serializers.ListField(
        child=serializers.CharField(),
        min_length=2,
        max_length=5,
    )
    days = serializers.IntegerField(default=30, min_value=7, max_value=365)


class PropertySearchSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, default='')
    area = serializers.CharField(required=False)
    developer = serializers.CharField(required=False)
    compound = serializers.CharField(required=False)
    property_type = serializers.ChoiceField(
        choices=['apartment', 'villa', 'townhouse', 'twin_house', 'duplex', 'penthouse', 'studio', 'chalet', ''],
        required=False, default='',
    )
    purpose = serializers.ChoiceField(choices=['sale', 'rent', 'new_launch', ''], required=False, default='')
    min_price = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    max_price = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    min_bedrooms = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    max_bedrooms = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    order_by = serializers.ChoiceField(
        choices=['-scraped_at', 'price', '-price', 'price_per_sqm', '-price_per_sqm'],
        required=False, default='-scraped_at',
    )
