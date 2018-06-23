from django.urls import path

from cart.api import views

app_name = 'cart'
urlpatterns = [
    path('cart', views.CartAPIView.as_view(), name='cart'),
    # path('checkout', views.CheckoutAPIView.as_view(), name='cart'),
    # path('checkout/finalize', views.CheckoutAPIView.as_view(), name='cart'),
]

