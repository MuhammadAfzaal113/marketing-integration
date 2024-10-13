from django.contrib import admin
from .models import Shop, Tag, CustomField, ContactTag


class ShopAdmin(admin.ModelAdmin):
    list_display = ('shop_id', 'shop_name', 'api_key')
    search_fields = ('shop_id', 'shop_name')


class TagAdmin(admin.ModelAdmin):
    list_display = ('shop', 'tag_name', 'tag_id')
    search_fields = ('tag_name',)
    list_filter = ('shop',)


class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('shop', 'field_name', 'field_id')
    search_fields = ('field_name',)
    list_filter = ('shop',)


class ContactTagAdmin(admin.ModelAdmin):
    list_display = ('shop', 'tag_name', 'tag_id')
    search_fields = ('tag_name',)
    list_filter = ('shop',)


admin.site.register(Shop, ShopAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(CustomField, CustomFieldAdmin)
admin.site.register(ContactTag, ContactTagAdmin)
