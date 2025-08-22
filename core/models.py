from idlelib.configdialog import tracers

from django.db import models
from django.db.models import SET_NULL
from django.utils import timezone
from accounting.models import Transaction, Accounting_Account, Journal


# Create your models here.

class Customer(models.Model):
    customer_name = models.CharField(max_length=30)
    owner_name = models.CharField(max_length=30)
    price_per_meter = models.IntegerField(default=0)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f' {self.customer_name} - {self.owner_name}'

class Delivered(models.Model):
    account = models.ForeignKey(Accounting_Account, on_delete=models.CASCADE, null=True) # account Receivable
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    price_per_meter = models.IntegerField(default=0)
    delivered = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(
        self,
        *args,
        **kwargs
    ):
        if self.pk is None:  # or if self._state.adding
            # This is a new object being created (INSERT)
            self.amount = self.price_per_meter * self.delivered
            t = Transaction.objects.create(description=f'Order Delivered For {self.customer.customer_name}', reference =f'customer-{self.customer.customer_name}', is_approved=True)
            j = Journal.objects.create( account = self.account,transaction=t,debit=self.amount)
            acc = Accounting_Account.objects.get(pk=4)
            j1 = Journal.objects.create( account = acc,transaction=t,credit=self.amount) # credit rev account
            self.transaction = t
            print("Creating a new MyModel instance.")
        else:
            # This is an existing object being updated (UPDATE)

            j = Journal.objects.get(transaction=self.transaction, credit=0)
            j.debit = self.amount # update ar account
            j.save()
            j1 = Journal.objects.get(transaction=self.transaction, debit=0)
            j1.credit = self.amount # update rev account
            j1.save()
            print(f"Updating MyModel instance with primary key: {self.pk}")

        super().save(*args, **kwargs)  # Call the original save method

    def delete(self, *args, **kwargs):
        # Delete the related User object before deleting the Profile object
        self.transaction.delete()
        # Call the original delete method to delete the Profile object
        return super().delete(*args, **kwargs)



class Payment(models.Model):
    account = models.ForeignKey(Accounting_Account, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    transaction = models.OneToOneField(Transaction, blank=True, null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(
        self,
        *args,
        **kwargs
    ):
        if self.pk is None:  # or if self._state.adding
            # This is a new object being created (INSERT)
            t = Transaction.objects.create(description=f'Payment Received From {self.customer.customer_name}', reference =f'customer-{self.customer.customer_name}', is_approved=True)
            # enter debit amount into assets
            j = Journal.objects.create( account = self.account,transaction=t,debit=self.amount)
            acc = Accounting_Account.objects.get(pk=4) # Revenue will be credited
            j1 = Journal.objects.create( account = acc,transaction=t,credit=self.amount)
            self.transaction = t
            print("Creating a new MyModel instance.")
        else:
            # This is an existing object being updated (UPDATE)
            j = Journal.objects.get(transaction=self.transaction, credit=0)
            j.debit = self.amount
            j.save()
            j1 = Journal.objects.get(transaction=self.transaction, debit=0)
            j1.credit = self.amount
            j1.save()
            print(f"Updating MyModel instance with primary key: {self.pk}")

        super().save(*args, **kwargs)  # Call the original save method

    def delete(self, *args, **kwargs):
        # Delete the related User object before deleting the Profile object
        self.transaction.delete()
        # Call the original delete method to delete the Profile object
        return super().delete(*args, **kwargs)


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

class Bill(models.Model):
    account = models.ForeignKey(Accounting_Account, on_delete=models.CASCADE, null=True) # account Payable
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    bill_id = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(
        self,
        *args,
        **kwargs
    ):
        if self.pk is None:  # or if self._state.adding
            # This is a new object being created (INSERT)
            #self.amount = self.price_per_meter * self.delivered
            t = Transaction.objects.create(description=f'Bill received From {self.supplier.company_name}', reference =f'supplier-{self.id}', is_approved=True)
            j = Journal.objects.create( account = self.account,transaction=t,credit=self.amount)
            acc = Accounting_Account.objects.get(pk=1)
            j1 = Journal.objects.create( account = acc,transaction=t,debit=self.amount) # credit rev account
            self.transaction = t
            print("Creating a new MyModel instance.")
        else:
            # This is an existing object being updated (UPDATE)

            j = Journal.objects.get(transaction=self.transaction, credit=0)
            j.debit = self.amount # update ar account
            j.save()
            j1 = Journal.objects.get(transaction=self.transaction, debit=0)
            j1.credit = self.amount # update rev account
            j1.save()
            print(f"Updating MyModel instance with primary key: {self.pk}")

        super().save(*args, **kwargs)  # Call the original save method

    def delete(self, *args, **kwargs):
        # Delete the related User object before deleting the Profile object
        self.transaction.delete()
        # Call the original delete method to delete the Profile object
        return super().delete(*args, **kwargs)

class SupplierPayment(models.Model):
    account = models.ForeignKey(Accounting_Account, on_delete=models.CASCADE, null=True) # Asset Account Credit
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(
        self,
        *args,
        **kwargs
    ):
        if self.pk is None:  # or if self._state.adding
            # This is a new object being created (INSERT)
            t = Transaction.objects.create(description=f'Payment Done to {self.supplier.company_name}', reference =f'supplier-{self.supplier.id}', is_approved=True)
            j = Journal.objects.create( account = self.account,transaction=t,credit=self.amount)
            acc = Accounting_Account.objects.get(pk=8)
            j1 = Journal.objects.create( account = acc,transaction=t,debit=self.amount)
            self.transaction = t
            print("Creating a new MyModel instance.")
        else:
            # This is an existing object being updated (UPDATE)
            j = Journal.objects.get(transaction=self.transaction, credit=0)
            j.debit = self.amount
            j.save()
            j1 = Journal.objects.get(transaction=self.transaction, debit=0)
            j1.credit = self.amount
            j1.save()
            print(f"Updating MyModel instance with primary key: {self.pk}")

        super().save(*args, **kwargs)  # Call the original save method

    def delete(self, *args, **kwargs):
        # Delete the related User object before deleting the Profile object
        self.transaction.delete()
        # Call the original delete method to delete the Profile object
        return super().delete(*args, **kwargs)


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