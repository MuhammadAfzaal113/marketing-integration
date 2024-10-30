import uuid
import json
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from webhook_integrate.models import Webhook, Shop, WebhookFilter
from utils.helper import json_reader, create_contact_via_api, RequestData, WebhookAction


@csrf_exempt
def shopmonkey_webhook(request, shop_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_url = request.build_absolute_uri()
            webhook = Webhook.objects.filter(webhook_url=full_url).first()
            if not webhook:
                return Response({'success': False, 'message': 'Webhook not found'}, status.HTTP_400_BAD_REQUEST)
            
            RequestData.objects.create(webhook=webhook, data=data)
            if webhook.apply_filters(data, is_and=True) or webhook.apply_filters(data, is_or=True):
                shop = Shop.objects.filter(shop_id=shop_id).first()
                if not shop:
                    return JsonResponse({"error": "Shop not found"}, status=200)

                action = WebhookAction.objects.filter(webhook=webhook).first()
                
                customer_email = json_reader(data, str(action.email))
                customer_phone = json_reader(data, str(action.phone))
                first_name = json_reader(data, str(action.first_name))
                last_name = json_reader(data, str(action.last_name))
                creation_date = json_reader(data, str(action.creation_date))
                total_cost = json_reader(data, str(action.total_cost))
                is_paid = json_reader(data, str(action.is_paid))
                is_invoice = json_reader(data, str(action.is_invoice))
                
                custom_fields = {
                    ['custom_fields']['is_paid']: str(is_paid) if is_paid else 'False',
                    ['custom_fields']['is_invoice']: str(is_invoice) if is_invoice else 'False',
                    ['custom_fields']['total_cost']: str(total_cost),
                    ['custom_fields']['creation_date']: str(creation_date)
                }

                customer_name = first_name + " " + last_name if first_name and last_name else ""
                public_id = json_reader(data, "publicId")
                if first_name and last_name and customer_phone and public_id:
                    contact_id = create_contact_via_api(customer_email, customer_phone, customer_name, custom_fields, tags, shop.api_key)

                    if contact_id:
                        return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
            else:
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
        webhook_filters = request.data.get('webhook_filters', None)
        
        webhook_id = request.data.get('webhook_id')
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'message': 'Webhook not found'}, status.HTTP_400_BAD_REQUEST)
        
        if not webhook_filter:
            return Response({'success': False, 'message': 'Filters not found'}, status.HTTP_400_BAD_REQUEST)
            
        webhook_filters = json.dumps(webhook_filters)
        for webhook_filter in webhook_filters:
            key = webhook_filter.get('key')
            value = webhook_filter.get('value')
            operator = webhook_filter.get('operator')
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
    
@api_view(['POST'])
def create_action(request):
    try:
        webhook_id = request.data.get('webhook_id')
        webhook = Webhook.objects.filter(id=webhook_id).first()
        if not webhook:
            return Response({'success': False, 'message': 'Webhook not found'}, status.HTTP_400_BAD_REQUEST)
        
        email = request.data.get('email', None)
        phone = request.data.get('phone', None)
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        creation_date = request.data.get('creation_date', None)
        total_cost = request.data.get('total_cost', None)
        is_paid = request.data.get('is_paid', None)
        is_invoice = request.data.get('is_invoice', None)
        customFields = json.loads(request.data.get('customFields', None))
        
        action = WebhookAction.objects.create(webhook=webhook, email=email, phone=phone, first_name=first_name, last_name=last_name, creation_date=creation_date, total_cost=total_cost, is_paid=is_paid, is_invoice=is_invoice, customFields=customFields)
        return Response({'success': True, 'message': 'Action created successfully', 'data': action.id}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def update_action(request):
    try:
        action_id = request.data.get('action_id')
        action = WebhookAction.objects.filter(id=action_id).first()
        if not action:
            return Response({'success': False, 'message': 'Action not found'}, status.HTTP_400_BAD_REQUEST)
        
        action.email = request.data.get('email', action.email)
        action.phone = request.data.get('phone', action.phone)
        action.first_name = request.data.get('first_name', action.first_name)
        action.last_name = request.data.get('last_name', action.last_name)
        action.creation_date = request.data.get('creation_date', action.creation_date)
        action.total_cost = request.data.get('total_cost', action.total_cost)
        action.is_paid = request.data.get('is_paid', action.is_paid)
        action.is_invoice = request.data.get('is_invoice', action.is_invoice)
        action.customFields = request.data.get('customFields', action.customFields)
        action.save()
        return Response({'success': True, 'message': 'Action updated successfully', 'data': action.id}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def update_filter(request):
    try:
        filter_id = request.data.get('filter_id')
        webhook_filter = WebhookFilter.objects.filter(id=filter_id).first()
        if not webhook_filter:
            return Response({'success': False, 'message': 'Filter not found'}, status.HTTP_400_BAD_REQUEST)
        
        webhook_filter.key = request.data.get('key', webhook_filter.key)
        webhook_filter.value = request.data.get('value', webhook_filter.value)
        webhook_filter.operator = request.data.get('operator', webhook_filter.operator)
        webhook_filter.save()
        return Response({'success': True, 'message': 'Filter updated successfully', 'data': filter.id}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def delete_action(request):
    try:
        action_id = request.GET.get('action_id')
        action = WebhookAction.objects.filter(id=action_id).first()
        if not action:
            return Response({'success': False, 'message': 'Action not found'}, status.HTTP_400_BAD_REQUEST)
        
        action.delete()
        return Response({'success': True, 'message': 'Action deleted successfully'}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def delete_filter(request):
    try:
        filter_id = request.GET.get('filter_id')
        webhook_filter = WebhookFilter.objects.filter(id=filter_id).first()
        if not webhook_filter:
            return Response({'success': False, 'message': 'Filter not found'}, status.HTTP_400_BAD_REQUEST)
        
        webhook_filter.delete()
        return Response({'success': True, 'message': 'Filter deleted successfully'}, status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status.HTTP_400_BAD_REQUEST)