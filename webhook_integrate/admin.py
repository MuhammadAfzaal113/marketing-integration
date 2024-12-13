from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Shop, Webhook, Tag, CustomField, ContactTag, FilterKeys
import uuid


# Admin form for Webhook with custom URL generation logic
class WebhookModelForm(forms.ModelForm):
    class Meta:
        model = Webhook
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        generate_v1_url = reverse('generate_webhook_url')
        generate_v2_url = reverse('generate_webhook_v2_url')

        # Configure the webhook_url field
        self.fields['webhook_url'].widget = forms.TextInput(attrs={
            'size': 80,
            'style': 'width: 70%; display: inline-block;',
            'readonly': True,
        })
        self.fields['webhook_url'].help_text = mark_safe(
            f'<button type="button" style="cursor: pointer; padding: 10px 15px; margin: 4px; color: #fff; '
            f'background: #417690; border: none; border-radius: 4px; transition: background 0.15s;" '
            f'onclick="generateWebhookUrl(\'{generate_v1_url}\')">Generate V1</button>'
            f'<button type="button" style="cursor: pointer; padding: 10px 15px; margin: 4px; color: #fff; '
            f'background: #17a589; border: none; border-radius: 4px; transition: background 0.15s;" '
            f'onclick="generateWebhookUrl2(\'{generate_v2_url}\')">Generate V2</button>'
            f'<script>'
            f'function generateWebhookUrl(url) {{'
            f'    fetch(url, {{ method: "POST" }})'
            f'        .then(response => response.json())'
            f'        .then(data => {{'
            f'            document.getElementById("id_webhook_url").value = data.url;'
            f'        }});'
            f'}}'
            f'function generateWebhookUrl2(url) {{'
            f'    fetch(url, {{ method: "POST" }})'
            f'        .then(response => response.json())'
            f'        .then(data => {{'
            f'            document.getElementById("id_webhook_url").value = data.url;'
            f'        }});'
            f'}}'
            f'</script>'
        )



# Admin classes with filters, search, and list displays for models
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('shop_id', 'shop_name', 'api_key')
    search_fields = ('shop_id', 'shop_name')


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    form = WebhookModelForm
    list_display = ('webhook_name', 'shop', 'webhook_url', 'is_filter')
    search_fields = ('webhook_url', 'webhook_name',)
    list_filter = ('shop', 'webhook_name',)
    actions = ['generate_webhook']

    def generate_webhook(self, request, queryset):
        for webhook in queryset:
            webhook.webhook_url = f"{uuid.uuid4()}"
            webhook.save()
        self.message_user(request, "Webhooks generated successfully.")

    generate_webhook.short_description = "Generate Webhook URL for selected webhooks"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag_uuid', 'webhook', 'tag_name', 'tag_id')
    search_fields = ('tag_name',)
    list_filter = ('tag_name',)


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('custom_uuid', 'webhook', 'field_name', 'field_id')
    search_fields = ('webhook',)
    list_filter = ('field_name',)


@admin.register(ContactTag)
class ContactTagAdmin(admin.ModelAdmin):
    list_display = ('contact_tag_uuid', 'webhook', 'tag_name', 'tag_id')
    search_fields = ('webhook',)
    list_filter = ('tag_name',)

@admin.register(FilterKeys)
class FIlterKeysAdmin(admin.ModelAdmin):
    list_display = ('webhook', 'first_name', 'last_name', 'email', 'phone', 'total', 'date')
    search_fields = ('webhook',)
    list_filter = ('first_name', 'last_name', 'email', 'phone')