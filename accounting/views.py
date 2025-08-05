from django.shortcuts import render
from unicodedata import category
from accounting.financial_reports import *
from accounting.models import Accounting_Account, Category
from django.utils import timezone
from datetime import datetime

# Create your views here.

def enter_income(req):
    return render(req, 'backend/accounting/income.html')


def enter_expense(req):
    return render(req, 'backend/accounting/expense_entry.html')


def income_statement(req):
    income_statement = generate_income_statement(
        from_date=timezone.make_aware(datetime(2023, 1, 1)),
        to_date=timezone.make_aware(datetime.now()),
        method='accrual'
    )

    return render(req, 'backend/accounting/income_statement.html', income_statement)

def income_statement_report(req):
    income_statement = generate_income_statement(
        from_date=timezone.make_aware(datetime(2023, 1, 1)),
        to_date=timezone.make_aware(datetime.now()),
        method='accrual'
    )

    return render(req, 'backend/accounting/income_statement_report.html', income_statement)


def balance_sheet(req):
    return render(req, 'backend/accounting/balance_sheet.html')

