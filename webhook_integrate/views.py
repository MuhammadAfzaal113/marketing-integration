import uuid
import json
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from webhook_integrate.models import *
import requests
from datetime import datetime
import uuid

# def env_var(shop_id):
#     env = {
#         '137c4887': {
#             'shop_name': 'speed_of_sound',
#             'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IjFiYVpjRTdUeHVaN1d3aXRlckt3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzI3Mzg3Nzk0ODAwLCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.QUDqnmQL3FXV33JsvbwvdI2EYtEDahZApBupU1QZkxI',
#             'tag_id': {
#                 '48hoursmsfollowup': '66f1e6a215e9cb493d3cb538',
#                 'firstTimeCustomer': '65a6dd414b3584bbdabe146d',
#             },
#             'custom_fields': {
#                 'is_paid': 'A27TucjoRyaGgmUenMBC',
#                 'is_invoice': 'miWOey9B79FmN9mlE111',
#                 'total_cost': 'mvQCVs9s0IjzgjvWML53',
#                 'creation_date': 'PpCU6yesCcheRmUd5Fss'
#             },
#             'contact_tag': {
#                 '48hrs': '48hoursmsfollowup',
#                 'firstTimeCustomer': 'firstTimeCustomer'
#             }
#         },
#         '111f3445': {
#             'shop_name': 'stereo_steve',
#             'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IlRUVHFPZHAxVk9oWmpIUVo0bFlKIiwiY29tcGFueV9pZCI6IlJLdWpCTUdDT0wyV0FvTHZnOHV3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzA0ODE5Njk0NzY2LCJzdWIiOiJ1c2VyX2lkIn0.gKTyfdF1jNSK3JsvPdVWlTy4PL0iPXdBnFv9g1A4ktU',
#             'tag_id': {
#                 'zaps': '65d7e284a86dea1d0419154c',
#                 '48hoursmsfollowup': '65d7e284a86dea1d0419154c',
#                 # '48hoursmsfollowup': '670a4aebf1ad447c77f2aa49',
#                 'firstTimeCustomer': '65a6dd414b3584bbdabe146d',
#             },
#             'custom_fields': {
#                 'is_paid': 'ZUigjdADYGCXXedkj8Mf',
#                 'is_invoice': '503wVKGF3wNQrfQjBQFQ',
#                 'total_cost': 'CcUfyOz4HDP9Y4tzkUrW',
#                 'creation_date': 'oqIj1JREs8BhljSQvejZ'
#             },
#             'contact_tag': {
#                 '48hrs': '(2)sm4followup',
#                 'firstTimeCustomer': 'firstTimeCustomer'
#             }
#         },
#         'fe7b41f8': {
#             'shop_name': 'capital_car_audio',
#             'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6ImVGMVhWdTd4YkFtZFMycXY4MmkwIiwidmVyc2lvbiI6MSwiaWF0IjoxNzI4NzU5NjgzNTk1LCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.-WY5h5gtM7Kak7d-XSeplJh2FQ7O678ALNIGOG10v0Q',
#             'tag_id': {
#                 '48hoursmsfollowup': '65d7e284a86dea1d0419154c',
#                 'firstTimeCustomer': '65a6dd414b3584bbdabe146d',
#             },
#             'custom_fields': {
#                 'is_paid': 'JLemlO9TI5TehrWjHx72',
#                 'is_invoice': 'tdJ1XUAHeGKIr0s5si8m',
#                 'total_cost': 'kTQQPVdVtV3uf81WAJc1',
#                 'creation_date': 'vgnwxi0kEUXTBgJTlM7j'
#             },
#             'contact_tag': {
#                 '48hrs': '48hoursmsfollowup',
#                 'firstTimeCustomer': 'firstTimeCustomer'
#             }
#         },
#
#         '513d1344': {
#                 'shop_name': 'bid_monster',
#         }
#     }
#     # invoiced True for Won filter
#     return env[shop_id]


def json_reader(json_data, key):
    if isinstance(json_data, dict):
        if key in json_data:
            return json_data[key]
        else:
            for value in json_data.values():
                result = json_reader(value, key)
                if result is not None:
                    return result
    elif isinstance(json_data, list):
        for item in json_data:
            result = json_reader(item, key)
            if result is not None:
                return result
    return None


def create_contact_via_api(email, phone, name, custom_fields, tags, api_key):
    url = "https://rest.gohighlevel.com/v1/contacts/"
    data = {
        'source': "AutoMojo API",
        'email': email,
        'phone': phone,
        'name': name,
        'firstName': name.split()[0] if name else "",
        'lastName': name.split()[1] if len(name.split()) > 1 else "",
        'tags': tags or [],
        'customField': custom_fields
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get("contact", {}).get("id")
    else:
        print(response.status_code, response.text)
        raise Exception("Failed to create contact via API")


@csrf_exempt
def shopmonkey_webhook(request, webhook_url):
    try:
        with open('data.txt', 'w') as f:
            f.write(str(request.build_absolute_uri()))
            f.write('\n')
    except Exception as e:
        print(e)
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        full_url = request.build_absolute_uri()
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        if not webhook:
            return JsonResponse({"error": "Webhook not found"}, status=404)

        api_key = str(webhook.shop.api_key)
        tags = Tag.objects.filter(webhook=webhook).first()
        custom_fields = CustomField.objects.filter(webhook=webhook)
        contact_tags = ContactTag.objects.filter(webhook=webhook) #get tag name list from contact tag model
        filter_keys = FilterKeys.objects.filter(webhook=webhook) #get user info from user info model
        data = json.loads(request.body)
        try:
            with open('data.json', 'a') as f:
                json.dump(data, f)
                f.write('\n')
        except Exception as e:
            print(e)
        if webhook_url == '513d1344':
            write_or_append_json(data)
            return JsonResponse({'status': 'success'}, status=200)
        
        if webhook.is_filter:
            # Extract tags dynamically from the incoming data based on ContactTag entries
            matching_tags = []
            for tag in tags:
                if json_reader(data, tag.tag_name):
                    matching_tags.append(tag.tag_name)

            # Continue only if relevant tags found in data
            if not matching_tags:
                return JsonResponse({'status': 'success'}, status=200)
            
        customer_email = json_reader(data, str(filter_keys.email))
        customer_phone = json_reader(data, str(filter_keys.phone))
        first_name = json_reader(data, str(filter_keys.first_name))
        last_name = json_reader(data, str(filter_keys.last_name))
        creation_date = json_reader(data, str(filter_keys.date))
        total_cost = json_reader(data, str(filter_keys.total))
        is_paid = json_reader(data, "isPaid")
        is_invoice = json_reader(data, "isInvoice")

        custom_field_map = {cf.field_name: cf.field_id for cf in custom_fields}
        custom_fields_data = {
            custom_field_map.get('is_paid'): str(is_paid) if is_paid else 'False',
            custom_field_map.get('is_invoice'): str(is_invoice) if is_invoice else 'False',
            custom_field_map.get('total_cost'): str(total_cost),
            custom_field_map.get('creation_date'): str(creation_date)
        }

        customer_name = f"{first_name} {last_name}".strip()
        contact_id = create_contact_via_api(
            email=customer_email,
            phone=customer_phone,
            name=customer_name,
            custom_fields=custom_fields_data,
            tags=tags,
            api_key=api_key
        )

        if contact_id:
            return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
        return JsonResponse({"error": "Invalid data"}, status=200)
    except Shop.DoesNotExist:
        return JsonResponse({"error": "Shop not found"}, status=404)
    except Exception as e:
        print({"error": str(e)})
        return JsonResponse({"error": str(e)}, status=500)


def write_or_append_json(data, file_path="data.json"):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {current_datetime: data}

    try:
        with open(file_path, "r") as file:
            json_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        json_data = []

    json_data.append(new_entry)

    with open(file_path, "w") as file:
        json.dump(json_data, file, indent=4)

# API to create a new webhook
@csrf_exempt
def create_webhook(request):
    if request.method == 'POST':
        generated_url = f"https://webhook.automojo.io/webhook/{str(uuid.uuid4()).split('-')[0]}"
        return JsonResponse({'url': generated_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def generate_webhook_url(request):
    if request.method == 'POST':
        generated_url = f"https://webhook.automojo.io/webhook/{uuid.uuid4()}"
        return JsonResponse({'webhook_url': generated_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)