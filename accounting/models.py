from django.db import models
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=30)
    sort = models.IntegerField(default=0, null=True, blank=True)
    type_choices = [
        ('A', 'Asset'),
        ('L', 'Liability'),
        ('E', 'Equity'),
        ('I', 'Income'),
        ('X', 'Expense'),
    ]
    category_type = models.CharField(max_length=1, choices=type_choices)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Accounting_Account(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=10, unique=True)
    sort = models.IntegerField(default=0, null=True, blank=True)
    category = models.ForeignKey(Category, related_name='accounts', null=True, on_delete=models.SET_NULL)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name} - {self.balance}"

    def get_balance(self):
        """
        Calculate current account balance based on all journal entries
        Returns a dictionary with debit, credit, and balance amounts
        """
        # Get sum of all debits and credits for this account
        result = self.journal_entries.aggregate(
            total_debit=Coalesce(Sum('debit'), Decimal('0')),
            total_credit=Coalesce(Sum('credit'), Decimal('0'))
        )


        # Determine balance based on account category type
        if self.category.category_type in ['A', 'X']:  # Assets and Expenses
            balance = self.opening_balance + result['total_debit'] - result['total_credit']
        else:  # Liabilities, Equity, and Income
            balance = self.opening_balance + result['total_credit'] - result['total_debit']

        return {
            'debit': result['total_debit'],
            'credit': result['total_credit'],
            'balance': balance
        }

    @property
    def balance(self):
        """Property to easily access the current balance"""
        return self.get_balance()['balance']


class Transaction(models.Model):
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    datetime = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=50, blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.date} - {self.description[:20]}"

    def save(self, *args, **kwargs):
        """Ensure the transaction is balanced before saving"""
        super().save(*args, **kwargs)
        if self.is_approved:
            self.update_account_balances()

    def update_account_balances(self):
        """Update all account balances affected by this transaction"""
        for journal in self.journal_entries.all():
            journal.account.get_balance()


class Journal(models.Model):
    account = models.ForeignKey(Accounting_Account, on_delete=models.CASCADE, related_name='journal_entries')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='journal_entries')
    ref    = models.CharField(blank=True, null=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['transaction__date', 'id']

    def __str__(self):
        return f"{self.transaction.date} - {self.account.name} (D: {self.debit}, C: {self.credit})"

    def clean(self):
        """Validate that either debit or credit is set, but not both"""
        from django.core.exceptions import ValidationError
        if self.debit and self.credit:
            raise ValidationError("Journal entry cannot have both debit and credit amounts")
        if not self.debit and not self.credit:
            raise ValidationError("Journal entry must have either debit or credit amount")

    def save(self, *args, **kwargs):
        """Ensure the journal entry is valid before saving"""
        self.full_clean()
        super().save(*args, **kwargs)