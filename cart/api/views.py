import pdb
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from supplier.models import Cycle

from cart.models import Cart, CartItem
from .serializers import CartItemSerializer, CheckoutSerializer, CartSerializer


class CartAPIView(APIView):
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    token_param = "token"
    cart = None

    def get(self, request, format=None):
        cart_obj, new_object = Cart.objects.new_or_get(request)
        serializer = CartSerializer(cart_obj).data
        return Response(serializer, status.HTTP_200_OK)

    def post(self, request, format=None):
        pdb.set_trace()
        product_id = request.POST.get('product_id', None)
        if product_id is not None:
            try:
                product_obj = Cycle.objects.get(id=product_id)
            except Cycle.DoesNotExist:
                pass
            cart_instance, created = Cart.objects.new_or_get(request)
            if product_obj in cart_instance.items.all():
                cart_instance.items.remove(product_obj)
                added = False
            else:
                cart_instance.items.add(product_obj)
                pdb.set_trace()
                added = True
            request.session['cart_items'] = cart_instance.items.count()
            data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_instance.items.count()
            }
            return Response(data, status.HTTP_200_OK)








