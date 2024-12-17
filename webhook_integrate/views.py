import uuid
import json
import requests
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from webhook_integrate.models import *
from datetime import datetime

from dblogs.models import DataBaseLogs
from utils.helper import json_reader, create_contact_via_api


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
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        if not webhook:
            return JsonResponse({"error": "Webhook not found"}, status=404)

        WebhookRequests.objects.create(webhook=webhook, request_data=data) # save request data to db
        
        api_key = str(webhook.shop.api_key)
        tags = Tag.objects.filter(webhook=webhook)
        custom_fields = CustomField.objects.filter(webhook=webhook)
        contact_tags = ContactTag.objects.filter(webhook=webhook).first().tag_id #get tag name list from contact tag model
        filter_keys = FilterKeys.objects.filter(webhook=webhook).first() #get user info from user info model
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
        
        # ---------- Check  if webhook is filter or not ---------------
        if webhook.is_filter:
            matching_tags = []
            for tag in tags:
                if json_reader(data, tag.tag_name):
                    matching_tags.append(tag)
                    
            # if not matching_tags then return success
            if not matching_tags:
                return JsonResponse({'status': 'success'}, status=200)
            
        # --------------- Collecting data from incoming request ----------------
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

        # ----------------- Create contact in GoHighLevel -----------------
        customer_name = f"{first_name} {last_name}".strip()
        contact_id = create_contact_via_api(
            email=customer_email,
            phone=customer_phone,
            name=customer_name,
            custom_fields=custom_fields_data,
            tags=contact_tags,
            api_key=api_key
        )
        
        # ----------------- Delete old requests More then 10 Record -----------------
        webhook_requests = WebhookRequests.objects.filter(webhook=webhook).order_by('-created_at')
        if webhook_requests.count() > 10:
            for request in webhook_requests[10:]:
                request.delete()
        
        if contact_id:
            return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
        return JsonResponse({"error": "Invalid data"}, status=200)
    except Exception as e:
        # --------------- Store Error in DataBaseLogs ----------------
        log_description = f"Failed to send data to GoHighLevel: {str(e)}"
        DataBaseLogs.objects.create(
            description=log_description,
            error=str(e),
            webhook_version='V1',
            level='error',
            action='failed'
        )

        return JsonResponse({"error": str(e)}, status=200)


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
def create_webhook_v2(request):
    if request.method == 'POST':
        generated_url = f"https://webhook.automojo.io/webhook/v2/{str(uuid.uuid4()).split('-')[0]}"
        return JsonResponse({'url': generated_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def shopmonkey_webhook_v2(request, webhook_url):
    try:
        with open('data.txt', 'w') as f:
            f.write(str(request.build_absolute_uri()))
            f.write('\n')
    except Exception as e:
        print(e)
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=200)

    try:
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        if not webhook:
            return JsonResponse({"error": "Webhook not found"}, status=200)

        api_key = str(webhook.shop.api_key)
        tags = Tag.objects.filter(webhook=webhook)
        custom_fields = CustomField.objects.filter(webhook=webhook)
        contact_tags = ContactTag.objects.filter(webhook=webhook) #get tag name list from contact tag model
        filter_keys = FilterKeys.objects.filter(webhook=webhook).first() #get user info from user info model
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
                    tag = json_reader(data, tag.tag_name)
                    matching_tags.append(tag)

            # Continue only if relevant tags found in data
            if not matching_tags:
                return JsonResponse({'status': 'success'}, status=200)
            
        # -------------------- Fetch customer data from incoming request --------------------    
        customer_id = json_reader(data, 'customerId')
        customer = Customer.objects.filter(customer_id=customer_id).first()
        if not customer:
                return JsonResponse({'error': 'Customer not found'}, status=200)
        
        # -------------------- Collecting data from incoming request --------------------
        creation_date = json_reader(data, str(filter_keys.date))
        total_cost = json_reader(data, str(filter_keys.total))
        is_paid = json_reader(data, "paid")
        is_invoice = json_reader(data, "invoiced")

        custom_field_map = {cf.field_name: cf.field_id for cf in custom_fields}
        custom_fields_data = {
            custom_field_map.get('is_paid'): str(is_paid) if is_paid else 'False',
            custom_field_map.get('is_invoice'): str(is_invoice) if is_invoice else 'False',
            custom_field_map.get('total_cost'): str(total_cost),
            custom_field_map.get('creation_date'): str(creation_date)
        }

        # -------------------- Create contact for GoHighLevel --------------------
        customer_name = f"{customer.first_name} {customer.last_name}".strip()
        contact_id = create_contact_via_api(
            email=customer.email,
            phone=customer.phone,
            name=customer_name,
            custom_fields=custom_fields_data,
            tags=matching_tags,
            api_key=api_key
        )
        
        # ---------------- Delete old requests More then 10 Record ----------------
        webhook_requests = WebhookRequests.objects.filter(webhook=webhook).order_by('-created_at')
        if webhook_requests.count() > 10:
            for request in webhook_requests[10:]:
                request.delete()

        if contact_id:
            return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
        return JsonResponse({"error": "Invalid data"}, status=200)
    except Exception as e:
        log_description = f"Failed to send data to GoHighLevel: {str(e)}"
        DataBaseLogs.objects.create(
            description=log_description,
            error=str(e),
            webhook_version='V2',
            level='error',
            action='failed'
        )
        return JsonResponse({"error": str(e)}, status=200)