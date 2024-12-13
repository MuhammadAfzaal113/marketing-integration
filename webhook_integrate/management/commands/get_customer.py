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
                'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaWQiOiI2MWY4NDExZmZlNjQ1ZmE5MzQwMTUzZjEiLCJpZCI6IjYxZjg0MTBkNTE1ZmYzNDExYzU4MjRlMyIsImxpZCI6IjYxZjg0MTFmZmU2NDVmYTkzNDAxNTNmMSIsInAiOiJ3ZWIiLCJyaWQiOiJ1YzEiLCJzYWQiOjAsInNpZCI6IjVkMGE5Y2JkZDg4YmZlNTEiLCJ0Y2lkIjoiNjFmODQxMWZmZTY0NWZhOTM0MDE1M2YxIiwidHVpZCI6IjYxZjg0MTBkNTE1ZmYzNDExYzU4MjRlMyIsImRhdGFTaGFyaW5nIjpmYWxzZSwiaGFzSHEiOmZhbHNlLCJvbmIiOjcsInBheSI6NiwiYXVkIjoic2hvcCIsImlzcyI6Imh0dHBzOi8vYXBpLnNob3Btb25rZXkuY2xvdWQiLCJpYXQiOjE3MzQwODg0NDMsImV4cCI6MTczNDE3NDg0M30.-ksMyOipgaUU8S4rw_QYF5cldx1QyiFlvoKXHHggor4',
                'cache-control': 'max-age=0',
                'content-type': 'application/json',
                'cookie': 'intercom-id-uq2tacb0=e956fa3e-8f16-4522-bea6-37f463d9fd08; intercom-device-id-uq2tacb0=964aa623-2a5d-4ca8-bf49-6b7834dac173; intercom-session-uq2tacb0=OW1GOU9SZnJYZWtUa2lVUnIvQmpybUFVVHE2TFQvQ0FlWkFCcHo0T0J4OGt1YjhmVnZqdEU5bjZCNE50czBGdC0tbzdObENmTi8xYU82K0NnNlJSa2c5UT09--488688099d48fe0be8a4542f44dcd7fc5c2834a4; director-session-id=5d0a9cbdd88bfe51; director-session-id=5d0a9cbdd88bfe51',
                'origin': 'https://app.shopmonkey.cloud',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
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
                "limit": 5000,
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
                    # import pdb; pdb.set_trace()
                    customer = Customer.objects.create(
                        customer_id = user.get('id', None),
                        first_name = user.get('firstName', None),
                        last_name = user.get('lastName', None),
                        phone = user.get('phoneNumbers', [{}])[0].get('number', None) if user.get('phoneNumbers', [{}])[0] else None,
                        email = user.get('emails', [{}])[0].get('email', None) if user.get('emails', None) else None
                        )
                    
                    print(f"Customer {customer.customer_id} created successfully")

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
        



            