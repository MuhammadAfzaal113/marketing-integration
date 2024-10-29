import uuid
import json
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from webhook_integrate.models import Webhook, Shop, WebhookFilter, Operators


def env_var(shop_id):
    env = {
        '137c4887': {
            'shop_name': 'speed_of_sound',
            'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IjFiYVpjRTdUeHVaN1d3aXRlckt3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzI3Mzg3Nzk0ODAwLCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.QUDqnmQL3FXV33JsvbwvdI2EYtEDahZApBupU1QZkxI',
            'tag_id': {
                '48hoursmsfollowup': '66f1e6a215e9cb493d3cb538',
                'firstTimeCustomer': '65a6dd414b3584bbdabe146d',
            },
            'custom_fields': {
                'is_paid': 'A27TucjoRyaGgmUenMBC',
                'is_invoice': 'miWOey9B79FmN9mlE111',
                'total_cost': 'mvQCVs9s0IjzgjvWML53',
                'creation_date': 'PpCU6yesCcheRmUd5Fss'
            },
            'contact_tag': {
                '48hrs': '48hoursmsfollowup',
                'firstTimeCustomer': 'firstTimeCustomer'
            }
        },
        '111f3445': {
            'shop_name': 'stereo_steve',
            'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IlRUVHFPZHAxVk9oWmpIUVo0bFlKIiwiY29tcGFueV9pZCI6IlJLdWpCTUdDT0wyV0FvTHZnOHV3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzA0ODE5Njk0NzY2LCJzdWIiOiJ1c2VyX2lkIn0.gKTyfdF1jNSK3JsvPdVWlTy4PL0iPXdBnFv9g1A4ktU',
            'tag_id': {
                'zaps': '65d7e284a86dea1d0419154c',
                '48hoursmsfollowup': '65d7e284a86dea1d0419154c',
                # '48hoursmsfollowup': '670a4aebf1ad447c77f2aa49',
                'firstTimeCustomer': '65a6dd414b3584bbdabe146d',
            },
            'custom_fields': {
                'is_paid': 'ZUigjdADYGCXXedkj8Mf',
                'is_invoice': '503wVKGF3wNQrfQjBQFQ',
                'total_cost': 'CcUfyOz4HDP9Y4tzkUrW',
                'creation_date': 'oqIj1JREs8BhljSQvejZ'
            },
            'contact_tag': {
                '48hrs': '(2)sm4followup',
                'firstTimeCustomer': 'firstTimeCustomer'
            }
        },
        'fe7b41f8': {
            'shop_name': 'capital_car_audio',
            'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6ImVGMVhWdTd4YkFtZFMycXY4MmkwIiwidmVyc2lvbiI6MSwiaWF0IjoxNzI4NzU5NjgzNTk1LCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.-WY5h5gtM7Kak7d-XSeplJh2FQ7O678ALNIGOG10v0Q',
            'tag_id': {
                '48hoursmsfollowup': '65d7e284a86dea1d0419154c',
                'firstTimeCustomer': '65a6dd414b3584bbdabe146d',
            },
            'custom_fields': {
                'is_paid': 'JLemlO9TI5TehrWjHx72',
                'is_invoice': 'tdJ1XUAHeGKIr0s5si8m',
                'total_cost': 'kTQQPVdVtV3uf81WAJc1',
                'creation_date': 'vgnwxi0kEUXTBgJTlM7j'
            },
            'contact_tag': {
                '48hrs': '48hoursmsfollowup',
                'firstTimeCustomer': 'firstTimeCustomer'
            }
        },
    }
    return env[shop_id]


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
    data = dict()
    data['source'] = "AutoMojo API"
    if email:
        data['email'] = email
    if phone:
        data['phone'] = phone
    if name:
        data['name'] = name
        data['firstName'] = name.split()[0]
        data['lastName'] = name.split()[1] if len(name.split()) > 1 else ""

    if tags is not []:
        data['tags'] = tags
    data['customField'] = custom_fields
    print("payload: ", data)
    payload = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()["contact"]["id"]
    else:
        print(response.status_code)
        print(response.text)
        raise Exception("Failed to create contact via API")


@csrf_exempt
def shopmonkey_webhook(request, shop_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if json_reader(data, "tags") is None:
                return JsonResponse({'status': 'success'}, status=200)
            env = env_var(shop_id)

            if env['tag_id']['48hoursmsfollowup'] in json_reader(data, "tags"):  # 48hrsSMSworkflow
                tags = env['contact_tag']['48hrs']
            elif env['tag_id']['firstTimeCustomer'] in json_reader(data, "tags"):  # firstTimeCustomer
                tags = env['contact_tag']['zaps']
            elif env['tag_id']['firstTimeCustomer'] in json_reader(data, "tags"):  # firstTimeCustomer
                tags = env['contact_tag']['firstTimeCustomer']
            else:
                return JsonResponse({'status': 'success'}, status=200)

            customer_email = json_reader(data, "customerEmail")
            customer_phone = json_reader(data, "customerPhone")
            first_name = json_reader(data, "firstName")
            last_name = json_reader(data, "lastName")
            creation_date = json_reader(data, "creationDate")
            total_cost = json_reader(data, "totalCost")
            is_paid = json_reader(data, "isPaid")
            is_invoice = json_reader(data, "isInvoice")

            custom_fields = {
                env['custom_fields']['is_paid']: str(is_paid) if is_paid else 'False',
                env['custom_fields']['is_invoice']: str(is_invoice) if is_invoice else 'False',
                env['custom_fields']['total_cost']: str(total_cost),
                env['custom_fields']['creation_date']: str(creation_date)
            }

            customer_name = first_name + " " + last_name if first_name and last_name else ""
            public_id = json_reader(data, "publicId")
            if first_name and last_name and customer_phone and public_id:
                contact_id = create_contact_via_api(customer_email, customer_phone, customer_name, custom_fields, tags, env['api_key'])

                if contact_id:
                    return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)

            return JsonResponse({"error": "Invalid data"}, status=200)
        except Exception as e:
            print({"error": str(e)})
            return JsonResponse({"error": str(e)}, status=200)
    print({"error": "Invalid request method"})
    return JsonResponse({"error": "Invalid request method"}, status=405)


@api_view(['GET'])
def generate_url(request):
    try:
        url = 'https://api.gohighlevel.com/v1/webhooks/'
        url = url + str(uuid.uuid4()).split('-')[0]
        
        webhook = Webhook.objects.create(webhook_url=url)
        response_data = {
            "success": True,
            "message": "Url Generate Successfully",
            "data": {
                "id": webhook.id,
                "webhook_url": webhook.webhook_url
            }
        }
        return Response({'success': True, 'message': 'Url Generate Successfully ', 'response_data':response_data,}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def create_filter(request):
    try:
        webhook_id = request.data.get('webhook_id')
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'message': 'Webhook not found'}, status.HTTP_400_BAD_REQUEST)
        else:
            key = request.data.get('key')
            value = request.data.get('value')
            operator = request.data.get('operator')
            webhook_filter = WebhookFilter.objects.create(webhook=webhook, key=key, value=value, operator=operator)
        return Response({'success': True, 'message': 'Filter created successfully', 'data': webhook_filter.id}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_webhook_list(request):
    try:
        webhook_id = request.query_params.get('webhook_id', None)
        if webhook_id:
            webhooks = Webhook.objects.filter(id=webhook_id).values('id', 'webhook_url')
        else:
            webhooks = Webhook.objects.values('id', 'webhook_url')
        return Response({'success': True, 'message': 'Webhook list', 'data': webhooks}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)