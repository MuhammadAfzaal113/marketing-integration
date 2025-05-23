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

from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from webhook_integrate.serializers import * 
from django.db.models import Q


@csrf_exempt
@permission_classes([AllowAny])
def shopmonkey_webhook(request, webhook_url):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        if not webhook:
            log_description = f"Webhook not found {webhook_url}"
            DataBaseLogs.objects.create(
            description=log_description,
            error=None,
            webhook_version='V1',
            level='warn',
            action='successful'
            )
            return JsonResponse({"error": "Webhook not found"}, status=404)
        
        if not webhook.is_active:
            return Response({'success': False, 'Message': 'Webhook is not active'}, status=status.HTTP_200_OK)

        WebhookRequests.objects.create(webhook=webhook, request_data=json.loads(request.body)) # save request data to db
        
        api_key = str(webhook.shop.api_key)
        tags = Tag.objects.filter(webhook=webhook)
        custom_fields = CustomField.objects.filter(webhook=webhook)
        contact_tags = ContactTag.objects.filter(webhook=webhook).first() #get tag name list from contact tag model
        filter_keys = FilterKeys.objects.filter(webhook=webhook).first() #get user info from user info model
        data = json.loads(request.body)
        
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
                log_description = f"Tag not found"
                DataBaseLogs.objects.create(
                webhook=webhook,
                description=log_description,
                error=None,
                webhook_version='V1',
                level='warn',
                action='successful'
                )
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

        custom_field_map = {cf.field_key: cf.field_value for cf in custom_fields}
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
            tags=list(custom_fields.values_list('field_value')),
            api_key=api_key
        )
        
        # ----------------- Delete old requests More then 10 Record -----------------
        webhook_requests = WebhookRequests.objects.filter(webhook=webhook).order_by('-created_at')
        if webhook_requests.count() > 10:
            for request in webhook_requests[10:]:
                request.delete()
        
        if contact_id:
            log_description = f"Data sent successfully to GoHighLevel: {contact_id}"
            DataBaseLogs.objects.create(
            webhook=webhook,
            description=log_description,
            error=None,
            webhook_version='V1',
            level='info',
            action='successful'
            )
            return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
        
        return JsonResponse({"error": "Invalid data"}, status=200)
    except Exception as e:
        # --------------- Store Error in DataBaseLogs ----------------
        log_description = f"Failed to send data to GoHighLevel: {str(e)}"
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        DataBaseLogs.objects.create(
            webhook=webhook,
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

@csrf_exempt
@permission_classes([AllowAny])
def shopmonkey_webhook_v2(request, webhook_url):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=200)

    try:
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        if not webhook:
            log_description = f"Webhook not found {webhook_url}"
            DataBaseLogs.objects.create(
            description=log_description,
            error=None,
            webhook_version='V2',
            level='warn',
            action='successful'
            )
            return JsonResponse({"error": "Webhook not found"}, status=200)
        
        if not webhook.is_active:
            return Response({'success': False, 'Message': 'Webhook is not active'}, status=status.HTTP_200_OK)
        
        WebhookRequests.objects.create(webhook=webhook, request_data=json.loads(request.body))

        api_key = str(webhook.shop.api_key)
        tags = Tag.objects.filter(webhook=webhook)
        custom_fields = CustomField.objects.filter(webhook=webhook)
        contact_tags = ContactTag.objects.filter(webhook=webhook) #get tag name list from contact tag model
        filter_keys = FilterKeys.objects.filter(webhook=webhook).first() #get user info from user info model
        data = json.loads(request.body)

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
                log_description = f"Tag not found"
                DataBaseLogs.objects.create(
                webhook=webhook,
                description=log_description,
                error=None,
                webhook_version='V2',
                level='warn',
                action='successful'
                )
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

        custom_field_map = {cf.field_key: cf.field_value for cf in custom_fields}
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
            tags=list(custom_fields.values_list('field_value')),
            api_key=api_key
        )
        
        # ---------------- Delete old requests More then 10 Record ----------------
        webhook_requests = WebhookRequests.objects.filter(webhook=webhook).order_by('-created_at')
        if webhook_requests.count() > 10:
            for request in webhook_requests[10:]:
                request.delete()

        if contact_id:
            log_description = f"Data sent successfully to GoHighLevel: {contact_id}"
            DataBaseLogs.objects.create(
                webhook=webhook,
                description=log_description,
                error=None,
                webhook_version='V2',
                level='info',
                action='successful'
            )
            return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
        
        return JsonResponse({"error": "Invalid data"}, status=200)
    except Exception as e:
        webhook = Webhook.objects.filter(webhook_url__contains=webhook_url).first()
        log_description = f"Failed to send data to GoHighLevel: {str(e)}"
        DataBaseLogs.objects.create(
            webhook=webhook,
            description=log_description,
            error=str(e),
            webhook_version='V2',
            level='error',
            action='failed'
        )
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
            return Response({'success': False, 'Message': 'Shop not found'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        shop_id = request.GET.get('shop_id')
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
        webhook_id = request.GET.get('webhook_id')
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
                    'results': serializer.data
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
        data = request.data
        
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
        data = request.data
        
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
        
        webhook_id = request.GET.get('webhook_id', None)
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        Tag.objects.filter(webhook_id=webhook_id).delete()
        
        return Response({'success': True, 'Message': 'Filter deleted successfully'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Filter not deleted due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def add_custom_field(request):
    try:
        data = request.data
        
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
                field_key=field.get('field_key', None), 
                field_value=field.get('field_value', None)
            )
        
        return Response({
            'success': True,
            'Message': 'Custom fields added successfully',
            'results': WebhookSerializer(webhook).data
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
        
        webhook_id = request.GET.get('webhook_id', None)
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

        webhook_id = request.GET.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        ContactTag.objects.filter(webhook_id=webhook_id).delete()
        
        return Response({'success': True, 'Message': 'Contact tags deleted successfully'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Contact tags not deleted due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_collect_data(request):
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
        
        return Response({
            'success': True,
            'Message': 'Filter keys created successfully',
            'results': WebhookSerializer(webhook).data
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Operation failed due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_collect_data(request):
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
def delete_collect_data(request):
    try:
        webhook_id = request.GET.get('webhook_id')
        if not webhook_id:
            return Response({'success': False, 'Message': 'Webhook ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        FilterKeys.objects.filter(webhook_id=webhook_id).delete()
        
        return Response({'success': True, 'Message': 'Filter keys deleted successfully'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'Message': f'Operation failed due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def generate_webhook_v1(request):
    try:
        generated_url = f"https://webhook.automojo.io/webhook/{str(uuid.uuid4()).split('-')[0]}"
        return Response({'success': True, 'message': "Webhook v1 URL generated successfully", 'url': generated_url}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'message': f'Operation failed due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def generate_webhook_v2(request):
    try:
        generated_url = f"https://webhook.automojo.io/webhook/v2/{str(uuid.uuid4()).split('-')[0]}"
        return Response({'success': True, 'message': "Webhook v2 URL generated successfully", 'url': generated_url}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'message': f'Operation failed due to {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
