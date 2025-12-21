from django.db import models
from django.conf import settings
from listings.models import Property

class Notification(models.Model):
    NOTIFICATION_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_CHOICES)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - Sent: {self.sent}"
