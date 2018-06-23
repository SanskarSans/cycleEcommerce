import pdb
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import UserCheckout, Order, UserAddress
from supplier.models import Cycle

from .mixins import TokenMixin, CartUpdateAPIMixin, CartTokenMixin
from cart.models import Cart, CartItem
from .serializers import CartItemSerializer, CheckoutSerializer, CartSerializer

#
# abc123

"""
{
    "order_token": "eydvcmRlcl9pZCc6IDU1LCAndXNlcl9jaGVja291dF9pZCc6IDExfQ==",
    "payment_method_nonce": "2bd23ca6-ae17-4bed-85f6-4d00aabcc3b0"

}


Run Python server:

python -m SimpleHTTPServer 8080

"""


class CheckoutFinalizeAPIView(TokenMixin, APIView):
    def get(self, request, format=None):
        response = {}
        order_token = request.GET.get('order_token')
        if order_token:
            checkout_id = self.parse_token(order_token).get("user_checkout_id")
            if checkout_id:
                checkout = UserCheckout.objects.get(id=checkout_id)
                client_token = checkout.get_client_token()
                response["client_token"] = client_token
                return Response(response)
        else:
            response["message"] = "This method is not allowed"
            return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # def post(self, request, format=None):
    #     data = request.data
    #     response = {}
    #     serializer = FinalizedOrderSerializer(data=data)
    #     if serializer.is_valid(raise_exception=True):
    #         request_data = serializer.data
    #         order_id = request_data.get("order_id")
    #         order = Order.objects.get(id=order_id)
    #         if not order.is_complete:
    #             order_total = order.order_total
    #             nonce = request_data.get("payment_method_nonce")
    #             if nonce:
    #                 result = braintree.Transaction.sale({
    #                     "amount": order_total,
    #                     "payment_method_nonce": nonce,
    #                     "billing": {
    #                         "postal_code": "%s" % (order.billing_address.zipcode),
    #
    #                     },
    #                     "options": {
    #                         "submit_for_settlement": True
    #                     }
    #                 })
    #                 success = result.is_success
    #                 if success:
    #                     # result.transaction.id to order
    #                     order.mark_completed(order_id=result.transaction.id)
    #                     # order.mark_completed(order_id="abc12344423")
    #                     order.cart.is_complete()
    #                     response["message"] = "Your order has been completed."
    #                     response["final_order_id"] = order.order_id
    #                     response["success"] = True
    #                 else:
    #                     # messages.success(request, "There was a problem with your order.")
    #                     error_message = result.message
    #                     # error_message = "Error"
    #                     response["message"] = error_message
    #                     response["success"] = False
    #         else:
    #             response["message"] = "Ordered has already been completed."
    #             response["success"] = False
    #
    #     return Response(response)


class CheckoutAPIView(TokenMixin, APIView):

    def post(self, request, format=None):
        data = request.data
        serializer = CheckoutSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
            user_checkout_id = data.get("user_checkout_id")
            cart_id = data.get("cart_id")
            billing_address = data.get("billing_address")
            shipping_address = data.get("shipping_address")

            user_checkout = UserCheckout.objects.get(id=user_checkout_id)
            cart_obj = Cart.objects.get(id=cart_id)
            s_a = UserAddress.objects.get(id=shipping_address)
            b_a = UserAddress.objects.get(id=billing_address)
            order, created = Order.objects.get_or_create(cart=cart_obj, user=user_checkout)
            if not order.is_complete:
                order.shipping_address = s_a
                order.billing_address = b_a
                order.save()
                order_data = {
                    "order_id": order.id,
                    "user_checkout_id": user_checkout_id
                }
                order_token = self.create_token(order_data)
        response = {
            "order_token": order_token
        }
        return Response(response)


class CartAPIView(CartTokenMixin, CartUpdateAPIMixin, APIView):
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    token_param = "token"
    cart = None

    def get_cart(self):
        data, cart_obj, response_status = self.get_cart_from_token()
        if cart_obj == None or not cart_obj.active:
            cart = Cart()
            cart.tax_percentage = 0.075
            if self.request.user.is_authenticated:
                cart.user = self.request.user
            cart.save()
            data = {
                "cart_id": str(cart.id)
            }
            self.create_token(data)
            cart_obj = cart

        return cart_obj

    def get(self, request, format=None):
        cart = self.get_cart()
        self.cart = cart
        # self.update_cart()
        # token = self.create_token(cart.id)
        items = CartItemSerializer(cart.cartitem_set.all(), many=True)
        cart.items.all()
        data = {
            "token": self.token,
            "cart": cart.id,
            "total": cart.total,
            "subtotal": cart.subtotal,
            "tax_total": cart.tax_total,
            "count": cart.items.count(),
            "items": items.data,
        }
        return Response(data)

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








