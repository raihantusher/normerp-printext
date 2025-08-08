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


    return render(req, 'backend/accounting/income_statement.html')

def income_statement_report(req):
    frm = req.GET.get('from')  # Get the value of the 'q' parameter
    to = req.GET.get('to')
    income_statement = generate_income_statement(
        from_date=timezone.make_aware(datetime(2023, 1, 1)),
        to_date=timezone.make_aware(datetime.now()),
        method='accrual'
    )

    return render(req, 'backend/accounting/income_statement_report.html', income_statement)


def balance_sheet(req):
    balance_sheet = generate_balance_sheet(
        as_of_date=timezone.make_aware(datetime.now())
    )
    return render(req, 'backend/accounting/balance_sheet.html', balance_sheet)



def trial_balance(req):
    trial_balance_period = generate_trial_balance(
        from_date=timezone.make_aware(datetime(2023, 1, 1)),
        to_date=timezone.make_aware(datetime.now())
    )
    print(trial_balance_period)
    return render(req, 'backend/accounting/trial_balance.html', trial_balance_period )
