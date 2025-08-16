from django.urls import path
from .views import Home, Customers
urlpatterns = [
    path('', Home, name='dashboard'),
    path('customers/', Customers, name='customers'),

]
