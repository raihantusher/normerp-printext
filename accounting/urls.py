from django.contrib import admin
from django.urls import path
from .views import enter_income

urlpatterns = [
    path('', enter_income, name="customer_payment")
]