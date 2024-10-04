from django.db import models

class Contact(models.Model):
    shopmonkey_id = models.CharField(max_length=255, unique=True)
    contact_id = models.CharField(max_length=255)

    def __str__(self):
        return self.name