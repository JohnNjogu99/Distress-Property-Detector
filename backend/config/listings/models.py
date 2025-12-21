from django.db import models
from django.conf import settings

# IMPORTANT: import scoring helpers
from .utils import calculate_distress_score, get_market_average_price


class Property(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    distress_score = models.FloatField(default=0.0)
    source = models.CharField(max_length=50, default="manual")  # CSV / API / manual
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Automatically calculate distress score on every save.
        """
        market_average = get_market_average_price(self.location)

        self.distress_score = calculate_distress_score(
            price=float(self.price),
            description=self.description,
            market_average=market_average
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.location}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"
