from rest_framework import viewsets
from inventory.models import *
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils.timezone import now


class OrderTransactionViewSet(viewsets.ModelViewSet):
    queryset = OrderTransaction.objects.all()
    serializer_class = OrderTransactionSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class DiningAreaViewSet(viewsets.ModelViewSet):
    queryset = DiningArea.objects.all()
    serializer_class = DiningAreaSerializer

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
class CurrentUserViewSet(APIView):
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class DashboardStatsView(APIView):
    def get(self, request):
        today = now().date()

        # OrderTransaction has a 'created' field
        total_orders = OrderTransaction.objects.filter(created=today).count()

        # OrderItem is linked to OrderTransaction via 'order'
        total_order_items = OrderItem.objects.filter(order__created=today).count()

        total_revenue = (
            OrderItem.objects.filter(order__created=today)
            .aggregate(total=Sum('total_price'))['total'] or 0
        )

        order_status_counts = (
            OrderItem.objects.filter(order__created=today)
            .values('status')
            .annotate(count=Count('id'))
        )

        return Response({
            "total_orders": total_orders,
            "total_order_items": total_order_items,
            "total_revenue": total_revenue,
            "order_status_counts": order_status_counts,
        })
