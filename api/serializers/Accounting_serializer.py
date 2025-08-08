from rest_framework import serializers

from accounting.models import Accounting_Account


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounting_Account
        fields = ['id', 'name', 'get_balance']



