from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from .models import Contact
from django.db import IntegrityError

# GoHighLevel Stages (Could also be stored in a database or fetched dynamically)
GOHIGHLEVEL_STAGES = [
    {"id": "efa68c90-eab5-4d55-b994-221b58b47e2d", "name": "In Conversation"},
    {"id": "e42d8387-bd53-4f55-a09a-181638cb8536", "name": "Steve Est. Needs Build "},
    {"id": "5cfe321c-3f50-4b96-88e4-b7aaa32568a2", "name": "Estimates"},
    {"id": "50fae1af-b111-457b-8501-ea42e99921e3", "name": "Follow up estimates "},
    {"id": "0aeebaa5-a398-41d6-aff5-70b600232e46", "name": "72 Hour Text Follow Up"},
    {"id": "056490d2-fadb-463b-8ba6-b5ad5a0500d4", "name": "10 Day Text Follow up"},
    {"id": "14a942f3-74a4-42a3-8608-5a9e4c611c71", "name": "21 Day Text Follow Up"},
    {"id": "c8d118bc-8319-4241-a5c0-2d6b66821157", "name": "60 Day Text Follow Up"},
    {"id": "100c2cdd-8b43-4de7-9a5e-5cfb6e11a14d", "name": "No Purchase / No Response"},
    {"id": "64c3d7ae-6f86-47d4-b38f-58332e990b74", "name": "Won"},
]


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


def get_stage_id_by_name(workflow_name):
    for stage in GOHIGHLEVEL_STAGES:
        if stage["name"].strip().lower() == workflow_name.strip().lower():
            return stage["id"]
    return None


def create_contact_via_api(email, phone, name):
    url = "https://rest.gohighlevel.com/v1/contacts/"
    data = dict()
    if email:
        data['email'] = email
    if phone:
        data['phone'] = phone
    if name:
        data['name'] = name
        data['firstName'] = name.split()[0]
        data['lastName'] = name.split()[1] if len(name.split()) > 1 else ""

    payload = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IjFiYVpjRTdUeHVaN1d3aXRlckt3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzI3Mzg3Nzk0ODAwLCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.QUDqnmQL3FXV33JsvbwvdI2EYtEDahZApBupU1QZkxI'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()["contact"]["id"]
    else:
        raise Exception("Failed to create contact via API")


def get_or_create_contact(public_id, email, phone, name):
    try:
        contact = Contact.objects.filter(shopmonkey_id=public_id).first()
        if contact:
            return contact.contact_id
        else:
            contact_id = create_contact_via_api(email, phone, name)

            new_contact = Contact(shopmonkey_id=public_id, contact_id=contact_id)
            new_contact.save()

            return contact_id
    except IntegrityError as e:
        print(f"Database error: {e}")
        return None


@csrf_exempt
def shopmonkey_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if '66f1e6a215e9cb493d3cb538' not in json_reader(data, "tags"):
                return JsonResponse({'status': 'success'}, status=200)

            # workflow_name = data[0]["mappings"]["workflow"]["name"]
            # customer_email = data[0]["data"].get("customerEmail", "")
            # customer_phone = data[0]["data"].get("customerPhone", "")
            # first_name = data[0]["mappings"]["customer"].get("firstName", "")
            # last_name = data[0]["mappings"]["customer"]["lastName"]
            customer_email = json_reader(data, "customerEmail")
            customer_phone = json_reader(data, "customerPhone")
            first_name = json_reader(data, "firstName")
            last_name = json_reader(data, "lastName")

            # customer_name = first_name + " " + last_name
            # customer_name is concatenated to avoid NoneType error
            customer_name = first_name + " " + last_name if first_name and last_name else ""
            public_id = json_reader(data, "publicId")
            if first_name and last_name and customer_phone and public_id:
                # stage_id = get_stage_id_by_name("48 Hour Text Follow Up")
                stage_id = '50fae1af-b111-457b-8501-ea42e99921e3'
                contact_id = get_or_create_contact(public_id, customer_email, customer_phone, customer_name)
                if stage_id:
                    payload = json.dumps({
                        "title": "new opportunity",
                        "status": "open",
                        "stageId": stage_id,
                        "email": customer_email,
                        "phone": customer_phone,
                        "contactId": contact_id,
                        "name": customer_name,
                        "tags": [
                            "48hoursmsfollowup",
                        ]
                    })
                    url = "https://rest.gohighlevel.com/v1/pipelines/myEIOmMlgBXbDm9y3zxH/opportunities/"
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IjFiYVpjRTdUeHVaN1d3aXRlckt3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzI3Mzg3Nzk0ODAwLCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.QUDqnmQL3FXV33JsvbwvdI2EYtEDahZApBupU1QZkxI'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload)

                    if response.status_code == 200:
                        print('success')
                        return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
                    else:
                        print({"error": str(response.text)})
                        return JsonResponse({"error": str(response.text)}, status=response.status_code)
                else:
                    print({"error": "No matching stage found"})
                    return JsonResponse({"error": "No matching stage found"}, status=200)

            return JsonResponse({"error": "Invalid data"}, status=200)
        except Exception as e:
            print({"error": str(e)})
            return JsonResponse({"error": str(e)}, status=200)
    print({"error": "Invalid request method"})
    return JsonResponse({"error": "Invalid request method"}, status=405)
