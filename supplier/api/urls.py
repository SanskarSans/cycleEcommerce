from django.urls import path

from supplier.api import views

app_name = 'supplier'
urlpatterns = [
    path('supplier', views.SupplierList.as_view(), name='supplier-list'),
    path('category', views.CategoryList.as_view(), name='category-list'),
    path('product', views.CycleList.as_view(), name='product-list'),
    path('product/<slug:slug>', views.CycleDetail.as_view(), name='product-detail'),
    path('product/category/<slug:slug>', views.CyclesOnCategory.as_view(), name='product-on-category'),
]

