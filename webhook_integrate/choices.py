from django.db import models
class Operators(models.TextChoices):
        EQUALS = 'equals', 'equals'
        CONTAINS = 'contains', 'contains'
        GTE = 'gte', 'gte'
        LTE = 'lte', 'lte'