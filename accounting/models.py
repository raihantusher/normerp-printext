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

    @property
    def is_debit_side(self):
        if self.category.category_type in ['A', 'X']:  # Assets and Expenses
            return True
        else:  # Liabilities, Equity, and Income
            return False

    def get_balance(self, from_date=None, to_date=None):
        """
        Calculate account balance, optionally filtered by date range
        Returns a dictionary with debit, credit, and balance amounts

        Args:
            from_date (date, optional): Start date of the period (inclusive)
            to_date (date, optional): End date of the period (inclusive)
        """
        # Filter journal entries if dates are provided
        journal_entries = self.journal_entries.all()

        if from_date and to_date:
            journal_entries = journal_entries.filter(date__range=[from_date, to_date])
        elif from_date:
            journal_entries = journal_entries.filter(date__gte=from_date)
        elif to_date:
            journal_entries = journal_entries.filter(date__lte=to_date)

        # Get sum of all debits and credits
        result = journal_entries.aggregate(
            total_debit=Coalesce(Sum('debit'), Decimal('0'), output_field=DecimalField()),
            total_credit=Coalesce(Sum('credit'), Decimal('0'), output_field=DecimalField())
        )

        # For date range, we typically want just the activity during the period
        if from_date or to_date:
            if self.category.category_type in ['A', 'X']:  # Assets and Expenses
                balance = result['total_debit'] - result['total_credit']
            else:  # Liabilities, Equity, and Income
                balance = result['total_credit'] - result['total_debit']
        else:
            # For full balance (no date range), include opening balance
            if self.category.category_type in ['A', 'X']:  # Assets and Expenses
                balance = self.opening_balance + result['total_debit'] - result['total_credit']
            else:  # Liabilities, Equity, and Income
                balance = self.opening_balance + result['total_credit'] - result['total_debit']

        return {
            'debit': result['total_debit'],
            'credit': result['total_credit'],
            'balance': balance,
            'is_period_balance': from_date is not None or to_date is not None
        }

    def get_balance_as_of(self, as_of_date):
        """Get balance up to and including a specific date (includes opening balance)"""
        return self.get_balance(to_date=as_of_date)

    def get_period_balance(self, from_date, to_date):
        """Get balance for a specific period only (excludes opening balance)"""
        return self.get_balance(from_date=from_date, to_date=to_date)

    @property
    def balance(self):
        """Property to easily access the current balance (all transactions)"""
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
    date = models.DateTimeField()
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