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


def get_stage_id_by_name(workflow_name):
    for stage in GOHIGHLEVEL_STAGES:
        if stage["name"].strip().lower() == workflow_name.strip().lower():
            return stage["id"]
    return None


def create_contact_via_api(email, phone, name):
    url = "https://rest.gohighlevel.com/v1/contacts/"

    payload = json.dumps({
        "email": email,
        "phone": phone,
        "firstName": name.split()[0],
        "lastName": name.split()[1] if len(name.split()) > 1 else "",
        "name": name
    })
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
            workflow_name = data[0]["mappings"]["workflow"]["name"]
            customer_email = data[0]["data"]["customerEmail"]
            customer_phone = data[0]["data"]["customerPhone"]
            customer_name = data[0]["mappings"]["customer"]["firstName"] + " " + data[0]["mappings"]["customer"][
                "lastName"]
            public_id = data[0]["data"]["publicId"]

            stage_id = get_stage_id_by_name(workflow_name)
            contact_id = get_or_create_contact(public_id, customer_email, customer_phone, customer_name)
            if stage_id:
                payload = json.dumps({
                    "title": "new opportunity",
                    "status": "open",
                    "stageId": stage_id,
                    "email": customer_email,
                    "phone": customer_phone,
                    "contactId": contact_id,
                    "name": customer_name
                })
                url = "https://rest.gohighlevel.com/v1/pipelines/myEIOmMlgBXbDm9y3zxH/opportunities/"
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IjFiYVpjRTdUeHVaN1d3aXRlckt3IiwidmVyc2lvbiI6MSwiaWF0IjoxNzI3Mzg3Nzk0ODAwLCJzdWIiOiJubDN3UFROSEhCM3Jtc1BNd3N2YiJ9.QUDqnmQL3FXV33JsvbwvdI2EYtEDahZApBupU1QZkxI'
                }
                response = requests.request("POST", url, headers=headers, data=payload)

                if response.status_code == 200:
                    return JsonResponse({"message": "Data sent successfully to GoHighLevel"}, status=200)
                else:
                    return JsonResponse({"error": "Failed to send data to GoHighLevel"}, status=response.status_code)
            else:
                return JsonResponse({"error": "No matching stage found"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
