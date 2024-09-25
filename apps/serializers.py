from rest_framework import serializers
from .models import CustomUser, Customer, SalesOrder


class CustomerSerializer(serializers.ModelSerializer):
   class Meta:
    model = Customer
    fields = '__all__'

class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = '__all__'
        

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['user_id', 'user_name', 'user_pw', 'ser_mail']

