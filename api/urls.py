
from rest_framework import routers
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CustomerList, CustomerDetail, AssetList, PaymentList
from django.views.decorators.csrf import csrf_exempt

router = routers.DefaultRouter(trailing_slash=False)
urlpatterns = [
    path('customers/', csrf_exempt(CustomerList.as_view()) ),
    path('customers/<int:pk>/', CustomerDetail.as_view()),


    path('cash-bank/', AssetList.as_view()),

    path('payment-list/', PaymentList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)