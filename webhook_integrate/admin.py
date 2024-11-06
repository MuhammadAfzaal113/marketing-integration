from django.contrib import admin
from .models import Shop, Tag, CustomField, ContactTag, Webhook
from django.utils.html import format_html
from django import forms
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.http import urlencode
import uuid


class ShopAdmin(admin.ModelAdmin):
    list_display = ('shop_id', 'shop_name', 'api_key')
    search_fields = ('shop_id', 'shop_name')


class TagAdmin(admin.ModelAdmin):
    list_display = ('tag_uuid', 'shop', 'tag_name', 'tag_id')
    search_fields = ('tag_name',)
    list_filter = ('shop',)


class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('custom_uuid', 'shop', 'field_name', 'field_id')
    search_fields = ('field_name',)
    list_filter = ('shop',)


class ContactTagAdmin(admin.ModelAdmin):
    list_display = ('contact_tag_uuid', 'shop', 'tag_name', 'tag_id')
    search_fields = ('tag_name',)
    list_filter = ('shop',)


class WebhookModelForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        generate_url = reverse('generate_webhook_url')
        self.fields['webhook_url'].widget = forms.TextInput(attrs={
            'size': 80,
            'style': 'width: 70%; display: inline-block;'
        })
        self.fields['webhook_url'].widget.attrs.update({
            'readonly': True,
        })
        self.fields['webhook_url'].help_text = mark_safe(
            f'<button type="button" style="cursor: pointer; padding: 10px 15px; margin: 4px; color: #fff; background: #417690; border: none; border-radius: 4px; transition: background 0.15s; " onclick="generateWebhookUrl()">Generate</button>'
            f'<script>'
            f'function generateWebhookUrl() {{'
            f'    fetch("{generate_url}", {{ method: "POST" }})'
            f'        .then(response => response.json())'
            f'        .then(data => {{'
            f'            document.getElementById("id_webhook_url").value = data.url;'
            f'        }});'
            f'}}'
            f'</script>'
        )


class WebhookAdmin(admin.ModelAdmin):
    form = WebhookModelForm
    list_display = ('webhook_name', 'shop', 'webhook_url')
    search_fields = ('webhook_url', 'webhook_name',)
    list_filter = ('shop', 'webhook_name',)
    actions = ['generate_webhook']

    def generate_webhook(self, request, queryset):
        for shop in queryset:
            webhook_url = str(uuid.uuid4()).split('-')[0]
            Webhook.objects.create(shop=shop, webhook_url=webhook_url)
        self.message_user(request, "Webhooks generated successfully.")

    generate_webhook.short_description = "Generate Webhook for selected shops"


admin.site.register(Webhook, WebhookAdmin)

admin.site.register(Shop, ShopAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(CustomField, CustomFieldAdmin)
admin.site.register(ContactTag, ContactTagAdmin)
