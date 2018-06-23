from rest_framework import serializers

from supplier.models import Supplier, Category, Cycle, Gallery


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = '__all__'


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = '__all__'


class CycleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cycle
        fields = '__all__'


class CycleDetailSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    category = CategorySerializer()
    gallery = GallerySerializer(read_only=True, many=True, source='gallery_set')

    class Meta:
        model = Cycle
        fields = ('supplier', 'category', 'gallery', 'name', 'slug', 'image', 'description', 'price',)
