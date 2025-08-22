from api.serializers.core_serializer import PaymentSerializer
from core.models import Payment
from rest_framework import generics
from api.serializers import PaymentSerializer

class PaymentList(generics.ListCreateAPIView):
    #queryset = Accounting_Account.objects.all()
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer