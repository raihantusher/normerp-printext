from django.contrib import admin
from django.urls import path
from .views import enter_income, enter_expense

urlpatterns = [
    path('/customer_payment/', enter_income, name="customer_payment"),
    path('/expense-entry/', enter_expense, name="enter_expense"),
]