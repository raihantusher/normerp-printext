from unicodedata import category

from accounting.models import Accounting_Account
from rest_framework import generics
from api.serializers import AssetSerializer

class AssetList(generics.ListAPIView):
    #queryset = Accounting_Account.objects.all()
    serializer_class = AssetSerializer

    def get_queryset(self):
        """"
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        category_ids = [ 2, 5] # bank and cash
        return Accounting_Account.objects.filter(category__id__in=category_ids)

