WEBHOOK_VERSION_CHOICES = (
    (1, 'V1'),
    (2, 'V2'),
)
log_types = dict((val, key) for key, val in WEBHOOK_VERSION_CHOICES)

LEVEL_TYPE_CHOICES = (
    (1, 'info'),
    (2, 'warn'),
    (3, 'error'),
    (4, 'fatal'),
)
level_types = dict((val, key) for key, val in LEVEL_TYPE_CHOICES)

ACTION_TYPE_CHOICES = (
    (1, 'failed'),
    (2, 'successful'),
)
action_types = dict((val, key) for key, val in ACTION_TYPE_CHOICES)
