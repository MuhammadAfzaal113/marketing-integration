from django.db import models


data = {'137c4887': {
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
}}


class Shop(models.Model):
    shop_id = models.CharField(max_length=255, unique=True)
    shop_name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return self.shop_name


class Tag(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name


class CustomField(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    field_id = models.CharField(max_length=255)

    def __str__(self):
        return self.field_name


class ContactTag(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name
