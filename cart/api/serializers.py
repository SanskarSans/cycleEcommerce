from rest_framework import serializers

from cart.models import Cart, CartItem
from supplier.models import Variation
from supplier.api.serializers import CycleSerializer
from order.models import UserAddress, UserCheckout

from .mixins import TokenMixin


class CheckoutSerializer(TokenMixin, serializers.Serializer):
    checkout_token = serializers.CharField()
    billing_address = serializers.IntegerField()
    shipping_address = serializers.IntegerField()
    cart_token = serializers.CharField()
    user_checkout_id = serializers.IntegerField(required=False)
    cart_id = serializers.IntegerField(required=False)

    def validate(self, data):
        checkout_token = data.get("checkout_token")
        billing_address = data.get("billing_address")
        shipping_address = data.get("shipping_address")
        cart_token = data.get("cart_token")

        cart_token_data = self.parse_token(cart_token)
        cart_id = cart_token_data.get("cart_id")

        checkout_data = self.parse_token(checkout_token)
        user_checkout_id = checkout_data.get("user_checkout_id")

        try:
            cart_obj = Cart.objects.get(id=int(cart_id))
            data["cart_id"] = cart_obj.id
        except:
            raise serializers.ValidationError("This is not a valid cart")

        try:
            user_checkout = UserCheckout.objects.get(id=int(user_checkout_id))
            data["user_checkout_id"] = user_checkout.id
        except:
            raise serializers.ValidationError("This is not a valid user")

        try:
            billing_obj = UserAddress.objects.get(user__id=int(user_checkout_id), id=int(billing_address))
        except:
            raise serializers.ValidationError("This is not a valid address for this user")

        try:
            shipping_obj = UserAddress.objects.get(user__id=int(user_checkout_id), id=int(shipping_address))
        except:
            raise serializers.ValidationError("This is not a valid address for this user")

        return data


class CartVariationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Variation
        fields = ('id', 'title', 'image')


class CartSerializer(serializers.ModelSerializer):
    user = serializers.CurrentUserDefault()
    # items = CycleSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['user', 'items', 'subtotal']


class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['items', 'quantity']


class CartItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()
    item_title = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "item",
            "item_title",
            "price",
            "product",
            "quantity",
            "line_item_total",
        ]

    @staticmethod
    def get_item(obj):
        return obj.item.id

    @staticmethod
    def get_item_title(self, obj):
        return '{0} {1}'.format(obj.item.product.title, obj.item.title)

    @staticmethod
    def get_product(self, obj):
        return obj.item.product.id

    @staticmethod
    def get_price(self, obj):
        return obj.item.price

