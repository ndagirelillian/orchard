from rest_framework import serializers
from inventory.models import *

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        # exclude = ['updated']
        read_only_fields = ['id', 'order_date', 'updated']


class OrderTransactionSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = OrderTransaction
        fields = '__all__'
        # exclude = ['created', 'updated', 'random_id']
        read_only_fields = ['id', 'created', 'updated', 'random_id']

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else None

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'dining_area', 'capacity', 'is_available']

class DiningAreaSerializer(serializers.ModelSerializer):
    tables = TableSerializer(many=True, read_only=True)

    class Meta:
        model = DiningArea
        fields = ['id', 'name', 'description', 'tables']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        
class CategorySerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = '__all__'
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']