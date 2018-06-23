from django.contrib import admin

from supplier.models import Supplier, Cycle, Category, Gallery


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'address', 'city', 'phone_number']
    prepopulated_fields = {'slug': ('name',)}
    # list_filter = ['available','created','updated']
    list_editable = ['phone_number', 'address', 'name']

    def __init__(self, *args, **kwargs):
        super(SupplierAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None


admin.site.register(Supplier, SupplierAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)


class CycleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'vote', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Cycle, CycleAdmin)

admin.site.register(Gallery)
