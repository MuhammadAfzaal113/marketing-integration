import json
import requests
from datetime import datetime

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