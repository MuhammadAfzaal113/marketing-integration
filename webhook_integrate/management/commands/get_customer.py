from django.core.management.base import BaseCommand
import requests
import json
from webhook_integrate.models import Customer

class Command(BaseCommand):
    help = 'Create Basic User Roles'

    def assign_permissions(self):
        try:
            url = 'https://api.shopmonkey.cloud/v3/customer/search'
            headers = {
                'accept': 'application/json',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaWQiOiI2MWY4NDExZmZlNjQ1ZmE5MzQwMTUzZjEiLCJpZCI6IjYxZjg0MTBkNTE1ZmYzNDExYzU4MjRlMyIsImxpZCI6IjYxZjg0MTFmZmU2NDVmYTkzNDAxNTNmMSIsInAiOiJ3ZWIiLCJyaWQiOiJ1YzEiLCJzYWQiOjAsInNpZCI6Ijc1OTNlY2I5OWJlOGJjMWUiLCJ0Y2lkIjoiNjFmODQxMWZmZTY0NWZhOTM0MDE1M2YxIiwiZGF0YVNoYXJpbmciOmZhbHNlLCJoYXNIcSI6ZmFsc2UsIm9uYiI6NywicGF5Ijo2LCJhdWQiOiJzaG9wIiwiaXNzIjoiaHR0cHM6Ly9hcGkuc2hvcG1vbmtleS5jbG91ZCIsImlhdCI6MTc0NTQ4MzE3NiwiZXhwIjoxNzQ1NTY5NTc2fQ.6C1vSm2ZOGVbZYrHsJ-zjUhQ6ZfY30H-94pgXkAFMsE',
                'cache-control': 'max-age=0',
                'content-type': 'application/json',
                'cookie': 'intercom-id-uq2tacb0=78d745da-4151-4053-a6da-1a21fef7e851; intercom-device-id-uq2tacb0=f8d78c97-1d9d-4741-be0a-17943c89540c; director-session-id=7593ecb99be8bc1e; intercom-session-uq2tacb0=dS9NTzRRWHgyYXczaXFuOHZVaFRvajYwazFlVzlJR3VLM1E1T3lkM0F4TUk1WUp1d3NMaW9lWVpaUUR1UGRGbmhXa3F6Z2F6NTRpTzZ3MFZiNDA3cWRBb1c1aFgxZlVpRWdoS000cC9KVWs9LS1obFQ3QytxOHp4LzJGMXNaMmJsVnlnPT0=--7ee2ec88bf05f35e9456d1312dfd51f651a0fdcc',
                'origin': 'https://app.shopmonkey.cloud',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'x-request-location': '/lists/customers'
            }

            data = {
                "where": {
                    "customerType": {
                        "equals": "Customer"
                    },
                    "createdDate": {
                        "period": "allTime"
                    }
                },
                "limit": 10000,
                "orderBy": {
                    "createdDate": "desc"
                },
                "skip": 0
            }

            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                response_data = json.loads(response.text)
                user_list = response_data.get('data', {})
                
                for user in user_list:
                    customer_id = user.get('id', None)
                    if Customer.objects.filter(customer_id=customer_id).exists():
                        pass
                    else:
                        try:
                            customer = Customer.objects.create(
                                customer_id = user.get('id', None),
                                first_name = user.get('firstName', None),
                                last_name = user.get('lastName', None),
                                phone = user.get('phoneNumbers', [{}])[0].get('number', None) if user.get('phoneNumbers', None) else None,
                                email = user.get('emails', [{}])[0].get('email', None) if user.get('emails', None) else None
                                )
                            print(f"Customer {customer.customer_id} created successfully")
                        except Exception as e:
                            self.stderr.write(f"Error: {e}")
                    
                    

        except Exception as e: # skip tenant for superuser or if error occurs
                self.stderr.write(f"Skipping due to error: {e}")
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
            
    def handle(self, *args, **kwargs):
        self.assign_permissions()
        self.stdout.write(self.style.SUCCESS('User Role Created successfully.'))
        



            