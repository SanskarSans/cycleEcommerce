from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from supplier.models import Supplier, Category, Cycle
from supplier.api.serializers import SupplierSerializer, CategorySerializer, CycleSerializer, CycleDetailSerializer


class SupplierList(ListAPIView):

    serializer_class = SupplierSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = Supplier.objects.all()
        return queryset


class CategoryList(ListAPIView):

    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset


class CycleList(ListAPIView):

    serializer_class = CycleSerializer

    def get_queryset(self):
        queryset = Cycle.objects.all()
        return queryset

class CyclesOnCategory(ListAPIView):

    serializer_class = CycleSerializer

    def get(self, request, *args, **kwargs):
        reply = {}
        print (kwargs)
        category = Category.objects.get(slug=kwargs.get('slug'))
        queryset = Cycle.objects.filter(category=category)
        reply['data'] = self.serializer_class(queryset, many=True).data
        return Response(reply, status.HTTP_200_OK)


class CycleDetail(RetrieveAPIView):

    serializer_class = CycleDetailSerializer
    queryset = Cycle.objects.all()
    lookup_field = 'slug'

