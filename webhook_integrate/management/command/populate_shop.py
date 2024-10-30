from django.core.management.base import BaseCommand
from webhook_integrate.models import Shop  

class Command(BaseCommand):
    help = 'Populate Shop data from env dictionary'

    def handle(self, *args, **kwargs):
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

        for shop_id, shop_data in env.items():
            shop = Shop.objects.create(
                shop_id=shop_id,
                shop_name=shop_data['shop_name'],
                api_key=shop_data['api_key'],
                tag_id=shop_data['tag_id'],
                custom_fields=shop_data['custom_fields'],
                contact_tag=shop_data['contact_tag']
            )
            self.stdout.write(f"shop: {shop.shop_name} (ID: {shop_id})")
