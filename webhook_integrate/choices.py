from django.db import models
class Operators(models.TextChoices):
        DOSENOTCONTAINS = 'does_not_contain', 'does_not_contain'
        CONTAINS = 'contains', 'contains'
        STARTWITH = 'start_with', 'start_with'
        NOTSTARTWITH = 'not_start_with', 'not_start_with'
        ENDSWITH = 'ends_with', 'ends_with'
        GREATER = 'greater', 'greater'
        LESS = 'less', 'less'
        AFTER = 'after', 'after'
        BEFORE = 'before', 'before'
        EQUALS = 'equals', 'equals'
        ISTRUE = 'is_true', 'is_true'
        ISFALSE = 'is_false', 'is_false'
        DOSENOTEXIST = 'does_not_exist', 'does_not_exist'
        EXISTS = 'exists', 'exists'