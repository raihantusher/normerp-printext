from idlelib.configdialog import tracers

from django.db import models
from django.db.models import SET_NULL
from django.utils import timezone
# Create your models here.

class Customer(models.Model):
    customr_name = models.CharField(max_length=30)
    owner_name = models.CharField(max_length=30)
    price_per_meter = models.IntegerField(default=0)
    remarks = models.TextField(blank=True, null=True)


class Supplier(models.Model):
    company_name = models.CharField(max_length=150)
    contact_person_name = models.CharField(max_length=150, null=True, blank=True)
    designation = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    contact_no = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    product = models.CharField(max_length=200)

    def __str__(self):
        return self.company_name

class Order(models.Model):
    customer = models.ForeignKey(Customer,null=True, on_delete=SET_NULL)
    qty = models.IntegerField()
    unit_price =models.IntegerField()
    total_amount = models.IntegerField()
    produced = models.IntegerField(default=0)
    delivered = models.IntegerField(default=0)
    total_paid_amount = models.IntegerField(default=0)
    remarks = models.CharField()
    date_time = models.DateTimeField(auto_now_add=True)

class PurchaseSublimationPaper(models.Model):
    supplier = models.ForeignKey(Supplier, null=True, on_delete=SET_NULL)
    paper_size = models.CharField(max_length=50)
    paper_description = models.CharField(max_length=200)
    gsm = models.PositiveIntegerField(help_text="Grams per square meter")
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        #self.balance = self.purchased - self.used
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.paper_description} ({self.paper_size}, {self.gsm} GSM)"



class PurchaseInk(models.Model):
    supplier = models.ForeignKey(Supplier, null=True, on_delete=SET_NULL)
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
        ('l', 'Liters'),
    ]

    ink_type = models.CharField(max_length=20, choices=INK_TYPE_CHOICES)
    ink_description = models.CharField(max_length=200)
    bottle_type = models.CharField(max_length=5, choices=BOTTLE_TYPE_CHOICES)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.balance = self.purchased - self.used
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_ink_type_display()} - {self.ink_description} ({self.bottle_type}L)"