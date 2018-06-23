from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import pre_save, post_save


class Supplier(models.Model):

    name = models.CharField(max_length=140, blank=False, null=False, db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=140, db_index=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    image = models.ImageField(upload_to='upload/supplier/%Y/%m/%d', blank=True)
    website = models.URLField(max_length=300, blank=True, null=True)
    facebook_page = models.URLField(max_length=200, blank=True, null=True)
    twitter_handle = models.CharField(max_length=15, blank=True, null=True)
    other_details = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )
        unique_together = (('id', 'name'),)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('suppliers:supplier-detail', args=[self.slug])


def create_slug(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = Supplier.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Supplier)


class Category(models.Model):

    name = models.CharField(max_length=120,db_index=True)
    slug = models.SlugField(max_length=120,db_index=True)
    image = models.ImageField(upload_to='upload/category/%Y/%m/%d', blank=True)
    description = models.TextField()

    class Meta:
        ordering=('name', )
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Cycle(models.Model):
    STARS = (
        (1, 'one'),
        (2, 'two'),
        (3, 'three'),
        (4, 'four'),
        (5, 'five'),
    )

    category = models.ForeignKey(Category, related_name='cycle', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(max_length=120, db_index=True)
    image = models.ImageField(upload_to='upload/cycle/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    vote = models.SmallIntegerField(choices=STARS, default=5)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Cycle'
        verbose_name_plural = 'Cycles'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('suppliers:product-detail', args=[self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(Cycle, related_name='productimages', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='upload/cycle/variation/%Y/%m/%d', blank=True)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "<Image: %d - %s>" % (self.id, self.product.title)


class Variation(models.Model):
    VAR_CATEGORIES = (
        ('color', 'color'),
    )
    product = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    category = models.CharField(max_length=120, choices=VAR_CATEGORIES, default='color')
    image = models.ForeignKey(ProductImage, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(null=True, blank=True)  # refer none == unlimited amount

    def __str__(self):
        return self.name

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def get_image(self):
        """if variation image available return its location else
        return its parents first image location"""
        if self.image:
            return self.image.image
        else:
            return self.product.productimages.first().image

    def add_to_cart(self):
        return '{0}?item={1}&qty=1'.format(reverse('carts:cart'), self.id)

    def remove_from_cart(self):
        return '{0}?item={1}&qty=1&delete=True'.format(reverse('carts:cart'), self.id)

    def get_title(self):
        return '{0} - {1}'.format(self.product.name, self.name)


def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.title = "Default"
        new_var.price = product.price
        new_var.save()


post_save.connect(product_post_saved_receiver, sender=Cycle)


class Gallery(models.Model):
    cycle = models.ForeignKey(Cycle, blank=False, null=False, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='upload/cycle/gallery/%Y/%m/%d', blank=True)
    caption = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'

    def __str__(self):
        return '{0} -{1}'.format(self.cycle.name, self.caption)


def create_slug_for_cycle(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = Cycle.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug_for_cycle(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug_for_cycle(instance)


pre_save.connect(pre_save_post_receiver, sender=Cycle)