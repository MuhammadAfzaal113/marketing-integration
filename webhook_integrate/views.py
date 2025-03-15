import uuid
import json
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from webhook_integrate.models import *
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from rest_framework import status
from webhook_integrate.serializers import *



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
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        if not webhook:
            return JsonResponse({"error": "Webhook not found"}, status=404)

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
        
        if webhook.is_filter:
            # Extract tags dynamically from the incoming data based on ContactTag entries
            matching_tags = []
            for tag in tags:
                if json_reader(data, tag.tag_name):
                    matching_tags.append(tag)

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
            tags=contact_tags,
            api_key=api_key
        )

        if contact_id:
            return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
        return JsonResponse({"error": "Invalid data"}, status=200)
    except Shop.DoesNotExist:
        return JsonResponse({"error": "Shop not found"}, status=404)
    except Exception as e:
        print({"error": str(e)})
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
            
        customer_id = json_reader(data, 'customerId')
        
        customer = Customer.objects.filter(customer_id=customer_id).first()
        
        if not customer:
                return JsonResponse({'error': 'Customer not found'}, status=200)
        
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

        customer_name = f"{customer.first_name} {customer.last_name}".strip()
        contact_id = create_contact_via_api(
            email=customer.email,
            phone=customer.phone,
            name=customer_name,
            custom_fields=custom_fields_data,
            tags=matching_tags,
            api_key=api_key
        )

        if contact_id:
            return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
        return JsonResponse({"error": "Invalid data"}, status=200)
    except Shop.DoesNotExist:
        return JsonResponse({"error": "Shop not found"}, status=200)
    except Exception as e:
        print({"error": str(e)})
        return JsonResponse({"error": str(e)}, status=200)
    
    
# ----------------------- New Webhook -----------------------
@api_view(['POST'])
def generate_webhook_v1(request):
    try:
        generated_url = f"https://webhook.automojo.io/webhook/{str(uuid.uuid4()).split('-')[0]}"
        return Response({'url': generated_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Webhook not generated due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def generate_webhook_v2(request):
    try:
        generated_url = f"https://webhook.automojo.io/webhook/v2/{str(uuid.uuid4()).split('-')[0]}"
        return Response({'url': generated_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Webhook not generated due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_shop(request):
    try:
        shop_name = request.data.get('shop_name')
        api_key = request.data.get('api_key')
        shop = Shop.objects.create(shop_name=shop_name, api_key=api_key)
        response_data = {
            'Success': True,
            'Message': 'shop created successfully',
            'id': str(shop.id)
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Shope not create due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def update_shop(request):
    try:
        data = request.data
        shop_id = data.get('shop_id')
        if not shop_id:
            return Response({'success': False, 'Message': 'Shop id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        shop = Shop.objects.filter(id=shop_id).first()
        if not shop:
            return Response({'success': False, 'Message': 'Shop not found'}, status=status.HTTP_400_NOT_FOUND)
        
        shop.shop_name = data.get('shop_name', shop.shop_name)
        shop.api_key = data.get('api_key', shop.api_key)
        shop.save()
        response_data = {
            'Success': True,
            'Message': 'shop updated successfully',
            'id': str(shop.id)
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Shop not updated due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def delete_shop(request):
    try:
        shop_id = request.data.get('shop_id')
        if not shop_id:
            return Response({'success': False, 'Message': 'Shop id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        shop = Shop.objects.filter(id=shop_id).first()
        if not shop:
            return Response({'success': False, 'Message': 'Shop not found'}, status=status.HTTP_400_NOT_FOUND)
        
        shop.delete()
        return Response({'success': True, 'Message': 'Shop deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Shop not deleted due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_shop(request):
    try:
        shop_id = request.GET.get('shop_id', None)
        search = request.GET.get('search', None)
        index = int(request.GET.get('index', 0))
        offset = int(request.GET.get('offset', 10))
        
        if shop_id:
            shop = Shop.objects.filter(id=shop_id).first()
            if not shop:
                return Response({'Success': False, 'Message': 'Shop not found'}, status=status.HTTP_400_NOT_FOUND)
            else:
                serializer = ShopSerializer(shop)
                response_data = {
                    'success': True,
                    'message': 'Shop found successfully by id',
                    'results': serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            query = Q()
            if search:
                query &= Q(shop_name__icontains=search)
            
            shops = Shop.objects.filter(query).order_by('-created_at')
            total = shops.count()
            
            if index and offset:
                shops = shops[index:index+offset]
            
            serializer = ShopSerializer(shops, many=True)
            response_data = {
                'success': True,
                'message': 'Shop found successfully',
                'total': total,
                'results': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Shop not found due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def create_webhook(request):
    try:
        data = request.data
        shop_id = data.get('shop_id', None)
        if not shop_id:
            return Response({'success': False, 'Message': 'Shop id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        shop = Shop.objects.filter(id=shop_id).first()
        if not shop:
            return Response({'success': False, 'Message': 'Shop not found'}, status=status.HTTP_400_NOT_FOUND)
        
        webhook_name = data.get('webhook_name', None)
        webhook_url = data.get('webhook_url', None)
        if not webhook_url:
            return Response({'success': False, 'Message': 'Webhook url is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_filter = data.get('is_filter', False)
        webhook = Webhook.objects.create(
            shop=shop, 
            webhook_name=webhook_name, 
            webhook_url=webhook_url, 
            is_filter=is_filter)
        
        response_data = {
            'Success': True,
            'Message': 'Webhook created successfully',
            'results': WebhookSerializer(webhook).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Webhook not create due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['PUT'])
def update_webhook(request):
    try:
        data = request.data
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_400_NOT_FOUND)
        
        webhook.webhook_name = data.get('webhook_name', webhook.webhook_name)
        webhook.webhook_url = data.get('webhook_url', webhook.webhook_url)
        webhook.is_filter = data.get('is_filter', webhook.is_filter)
        webhook.save()
        response_data = {
            'Success': True,
            'Message': 'Webhook updated successfully',
            'results': WebhookSerializer(webhook).data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Webhook not updated due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def delete_webhook(request):
    try:
        webhook_id = request.data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_400_NOT_FOUND)
        
        webhook.delete()
        return Response({'success': True, 'Message': 'Webhook deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Webhook not deleted due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_webhook(request):
    try:
        webhook_id = request.GET.get('webhook_id', None)
        search = request.GET.get('search', None)
        index = int(request.GET.get('index', 0))
        offset = int(request.GET.get('offset', 10))
        
        if webhook_id:
            webhook = Webhook.objects.filter(id=webhook_id).first()
            if not webhook:
                return Response({'Success': False, 'Message': 'Webhook not found'}, status=status.HTTP_400_NOT_FOUND)
            else:
                serializer = WebhookSerializer(webhook)
                response_data = {
                    'success': True,
                    'message': 'Webhook found successfully',
                    'results': [serializer.data]
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            query = Q()
            if search:
                query &= Q(webhook_name__icontains=search) | Q(shop__shop_name__icontains=search)
            
            webhooks = Webhook.objects.filter(query).order_by('-created_at')
            total = webhooks.count()
            
            if index and offset:
                webhooks = webhooks[index:index+offset]
            
            serializer = WebhookSerializer(webhooks, many=True)
            response_data = {
                'success': True,
                'message': 'Webhook found successfully',
                'total': total,
                'results': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'Message': f'Webhook not found due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def add_filter(request):
    try:
        data = requests.data
        
        webhook_id = data.get('webhook_id', None)
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_400_NOT_FOUND)
        
        tags = data.get('tags', [])
        for tag in tags:
            Tag.objects.create(webhook=webhook, tag_name=tag.get('tag_name'), tag_id=tag.get('tag_id'))
            
        response_data = {
            'success': True,
            'Message': 'Filter added successfully',
            'results': [WebhookSerializer(webhook).data]
        }
            
        return Response(response_data, status=status.HTTP_201_CREATED)
        
        
    except Exception as e:
        return Response({'success': False, 'Message': f'Filter not added due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def update_filter(request):
    try:
        data = requests.data
        
        webhook_id = data.get('webhook_id', None)
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_400_NOT_FOUND)
        
        Tag.objects.filter(webhook_id=webhook_id).delete()
        
        tags = data.get('tags', [])
        for tag in tags:
            Tag.objects.create(webhook_id=webhook_id, tag_name=tag.get('tag_name'), tag_id=tag.get('tag_id'))
            
        response_data = {
            'success': True,
            'Message': 'Filter updated successfully',
            'results': [WebhookSerializer(webhook).data]
        }    
            
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Filter not updated due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
api_view(['DELETE'])
def delete_filter(request):
    try:
        data = requests.data
        
        webhook_id = data.get('webhook_id', None)
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        Tag.objects.filter(webhook_id=webhook_id).delete()
        
        return Response({'success': True, 'Message': 'Filter deleted successfully'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Filter not deleted due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def add_custom_field(request):
    try:
        data = request.data  # Fixed from `requests.data` to `request.data`
        
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_404_NOT_FOUND)

        fields = data.get('fields', [])
        for field in fields:
            CustomField.objects.create(
                webhook=webhook, 
                field_key=field.get('field_key'), 
                field_value=field.get('field_value')
            )
        
        return Response({
            'success': True,
            'Message': 'Custom fields added successfully',
            'results': [WebhookSerializer(webhook).data]
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Custom fields not added due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_custom_field(request):
    try:
        data = request.data  # Fixed typo

        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_404_NOT_FOUND)

        # Delete existing custom fields
        CustomField.objects.filter(webhook_id=webhook_id).delete()

        # Add new custom fields
        fields = data.get('fields', [])
        for field in fields:
            CustomField.objects.create(
                webhook=webhook, 
                field_key=field.get('field_key'), 
                field_value=field.get('field_value')
            )

        return Response({
            'success': True,
            'Message': 'Custom fields updated successfully',
            'results': [WebhookSerializer(webhook).data]
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Custom fields not updated due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_custom_field(request):
    try:
        data = request.data  # Fixed typo
        
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        CustomField.objects.filter(webhook_id=webhook_id).delete()
        
        return Response({'success': True, 'Message': 'Custom fields deleted successfully'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Custom fields not deleted due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_contact_tag(request):
    try:
        data = request.data  # Fixed typo
        
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_404_NOT_FOUND)

        tags = data.get('tags', [])
        for tag in tags:
            ContactTag.objects.create(
                webhook=webhook, 
                tag_name=tag.get('tag_name'), 
                tag_value=tag.get('tag_value')
            )
        
        return Response({
            'success': True,
            'Message': 'Contact tags added successfully',
            'results': WebhookSerializer(webhook).data
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Contact tags not added due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
def update_contact_tag(request):
    try:
        data = request.data  # Fixed typo

        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_404_NOT_FOUND)

        # Delete existing contact tags
        ContactTag.objects.filter(webhook_id=webhook_id).delete()

        # Add new contact tags
        tags = data.get('tags', [])
        for tag in tags:
            ContactTag.objects.create(
                webhook=webhook, 
                tag_name=tag.get('tag_name'), 
                tag_value=tag.get('tag_value')
            )

        return Response({
            'success': True,
            'Message': 'Contact tags updated successfully',
            'results': WebhookSerializer(webhook).data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Contact tags not updated due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_contact_tag(request):
    try:
        data = request.data  # Fixed typo
        
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        ContactTag.objects.filter(webhook_id=webhook_id).delete()
        
        return Response({'success': True, 'Message': 'Contact tags deleted successfully'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Contact tags not deleted due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def upsert_filter_keys(request):
    try:
        data = request.data  # Fixed typo
        
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create or update the record in one operation
        filter_keys = FilterKeys.objects.create(
            webhook=webhook,
            first_name=data.get('first_name', None),
            last_name=data.get('last_name', None),
            email=data.get('email', None),
            phone=data.get('phone', None),
            total=data.get('total', None),
            date=data.get('date', None))
        message = 'Filter keys created successfully'
        
        return Response({
            'success': True,
            'Message': 'Filter keys created successfully',
            'results': WebhookSerializer(webhook).data
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Operation failed due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_filter_keys(request):
    try:
        data = request.data  # Fixed typo

        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'Message': 'Webhook not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update the existing record
        filter_keys = FilterKeys.objects.filter(webhook_id=webhook_id).first()
        if not filter_keys:
            return Response({'success': False, 'Message': 'Filter keys not found'}, status=status.HTTP_404_NOT_FOUND)

        filter_keys.first_name = data.get('first_name', filter_keys.first_name)
        filter_keys.last_name = data.get('last_name', filter_keys.last_name)
        filter_keys.email = data.get('email', filter_keys.email)
        filter_keys.phone = data.get('phone', filter_keys.phone)
        filter_keys.total = data.get('total', filter_keys.total)
        filter_keys.date = data.get('date', filter_keys.date)
        filter_keys.save()
        
        return Response({
            'success': True,
            'Message': 'Filter keys updated successfully',
            'results': WebhookSerializer(webhook).data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Operation failed due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['DELETE'])
def delete_filter_keys(request):
    try:
        data = request.data  # Fixed typo
        
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        FilterKeys.objects.filter(webhook_id=webhook_id).delete()
        
        return Response({'success': True, 'Message': 'Filter keys deleted successfully'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Operation failed due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)