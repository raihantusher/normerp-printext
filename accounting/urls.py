from django.contrib import admin
from django.urls import path
from .views import enter_income, enter_expense, income_statement, income_statement_report, balance_sheet

urlpatterns = [
    path('customer_payment/', enter_income, name="customer_payment"),
    path('expense-entry/', enter_expense, name="enter_expense"),
    path('income-statement/', income_statement, name="income_statement"),
    path('income-statement-report/', income_statement, name="income_statement_report"),
    path('balance-sheet/', balance_sheet, name="balance_sheet"),
]