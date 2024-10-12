from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests


def env_var(shop_id):
    env = {
        '137c4887': {
            'shop_name': 'speed_of_sound',
            'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IjFiYVpjRTdUeHVaN1d3aXRlckt3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzI3Mzg3Nzk0ODAwLCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.QUDqnmQL3FXV33JsvbwvdI2EYtEDahZApBupU1QZkxI',
            'tag_id': {
                '48hoursmsfollowup': '66f1e6a215e9cb493d3cb538',
                'firstTimeCustomer': '670a4aebf1ad447c77f2aa49',
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
            'api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IjFiYVpjRTdUeHVaN1d3aXRlckt3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzI3Mzg3Nzk0ODAwLCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.QUDqnmQL3FXV33JsvbwvdI2EYtEDahZApBupU1QZkxI',
            'tag_id': {
                '48hoursmsfollowup': '670a4aebf1ad447c77f2aa49',
                'firstTimeCustomer': '670a4aebf1ad447c77f2aa49',
            },
            'custom_fields': {
                'is_paid': 'A27TucjoRyaGgmUenMBC',
                'is_invoice': 'miWOey9B79FmN9mlE111',
                'total_cost': 'mvQCVs9s0IjzgjvWML53',
                'creation_date': 'PpCU6yesCcheRmUd5Fss'
            },
            'contact_tag': {
                '48hrs': '(2)sm4followup',
                'firstTimeCustomer': 'firstTimeCustomer'
            }

        },
        'fe7b41f8': {
            'shop_name': 'capital_car_audio',
            'api_key': '1111111111111111111111111111111111111111',
            'tag_id': {
                '48hoursmsfollowup': '670a4aebf1ad447c77f2aa49',
                'firstTimeCustomer': '670a4aebf1ad447c77f2aa49',
            },
            'custom_fields': {
                'is_paid': 'A27TucjoRyaGgmUenMBC',
                'is_invoice': 'miWOey9B79FmN9mlE111',
                'total_cost': 'mvQCVs9s0IjzgjvWML53',
                'creation_date': 'PpCU6yesCcheRmUd5Fss'
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
