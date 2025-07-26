from django.shortcuts import render


# Create your views here.

def enter_income(req):
    return render(req, 'backend/accounting/income.html')


def enter_expense(req):
    return render(req, 'backend/accounting/expense_entry.html')
