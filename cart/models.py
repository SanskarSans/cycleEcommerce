from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete

from supplier.models import Cycle, Variation


class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get('cart_id', None)
        cart_instance = self.get_queryset().filter(id=cart_id)
        if cart_instance.count() == 1:
            new_object = False
            cart_object = cart_instance.first()
            if request.user.is_authenticated and cart_object.user is None:
                cart_object.user = request.user
                cart_object.save()
        else:  # there is no any cart
            cart_object = Cart.objects.new(user=request.user)
            new_object = True
            request.session['cart_id'] = cart_object.id
        return cart_object, new_object

    def new(self, user=None):
        user_object = None
        if user is not None:
            if user.is_autenticated():
                user_object = user
        return self.model.objects.create(user=user_object)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    items = models.ManyToManyField(Variation, through='CartItem')
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    subtotal = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    tax_percentage = models.DecimalField(max_digits=10, decimal_places=5, default=0.085)
    tax_total = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)
    objects = CartManager()

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return str(self.id)

    def update_total(self):
        subtotal = 0
        items = self.cartitem_set.all()
        for item in items:
            subtotal += item.line_item_total
        self.subtotal = '%.2f'%(subtotal)
        self.save()

    def is_complete(self):
        self.active = False
        self.save()


def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
    subtotal = Decimal(instance.subtotal)
    tax_total = round(subtotal * Decimal(instance.tax_percentage), 2) #8.5%
    total = round(subtotal + Decimal(tax_total), 2)
    instance.tax_total = "%.2f" %(tax_total)
    instance.total = "%.2f" %(total)
    #instance.save()


pre_save.connect(do_tax_and_total_receiver, sender=Cart)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Variation, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    line_item_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        return self.cart.id

    def get_price(self):
        return self.item.price


def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if qty >= 1:
        price = instance.item.get_price()
        line_item_total = Decimal(qty) * Decimal(price)
        instance.line_item_total = line_item_total


pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)


def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
    instance.cart.update_subtotal()


post_save.connect(cart_item_post_save_receiver, sender=CartItem)

post_delete.connect(cart_item_post_save_receiver, sender=CartItem)
