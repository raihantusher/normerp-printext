from django.db import models
from django.utils import timezone


class SublimationPaper(models.Model):

    paper_size = models.CharField(max_length=50)
    paper_description = models.CharField(max_length=200)
    gsm = models.PositiveIntegerField(help_text="Grams per square meter")
    purchased = models.IntegerField
    used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.balance = self.purchased - self.used
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.paper_description} ({self.paper_size}, {self.gsm} GSM)"


class Ink(models.Model):
    INK_TYPE_CHOICES = [
        ('sublimation', 'Sublimation Ink'),
        ('dtf', 'DTF Ink'),
    ]

    BOTTLE_TYPE_CHOICES = [
        ('0.5', '500ml'),
        ('1', '1L'),
        ('2', '2L'),
        ('5', '5L'),
        ('10', '10L'),
    ]

    UNIT_CHOICES = [
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
    ]

    ink_type = models.CharField(max_length=20, choices=INK_TYPE_CHOICES)
    ink_description = models.CharField(max_length=200)
    bottle_type = models.CharField(max_length=5, choices=BOTTLE_TYPE_CHOICES)
    purchased = models.DecimalField(max_digits=10, decimal_places=2)
    used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.balance = self.purchased - self.used
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_ink_type_display()} - {self.ink_description} ({self.bottle_type}L)"