import json
from datetime import datetime, timedelta

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from core.models import Setting
from .forms import *
from .models import *

# Global today's date in correct timezone
today = timezone.localdate()


# === DASHBOARD ===
@login_required(login_url='/user/login/')
def dashboard(request):
    start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_today = timezone.make_aware(datetime.combine(today + timedelta(days=1), datetime.min.time()))

    orderTodayCount = OrderItem.objects.filter(order_date__range=(start_of_today, end_of_today)).count()
    orderCount = OrderItem.objects.count()
    today_total_amount = OrderItem.objects.filter(order_date__range=(start_of_today, end_of_today)).aggregate(total=Sum('total_price'))['total'] or 0
    orders = OrderItem.objects.select_related('menu_item').order_by('-order_date')[:5]

    return render(request, "dashboard.html", {
        "orderTodayCount": orderTodayCount,
        "orderCount": orderCount,
        "orders": orders,
        "today_total_amount": today_total_amount,
    })


# === MENU ===
@login_required(login_url='/user/login/')
def menu(request):
    menu_items = MenuItem.objects.select_related('category').all()
    return render(request, "menuitem_list.html", {"menu_items": menu_items})


def load_menu_items(request):
    category_id = request.GET.get('category')
    menu_items = MenuItem.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(menu_items), safe=False)


# === ORDERS ===
@login_required(login_url='/user/login/')
def orders(request):
    # Set the time range
    now_time = timezone.now()
    filter_time = now_time - timedelta(hours=12)

    # Query orders
    all_orders_count = OrderItem.objects.count()
    recent_orders = OrderItem.objects.filter(
        order_date__gte=filter_time
    ).select_related('order', 'table', 'dining_area').order_by('-order_date')
    recent_orders_count = recent_orders.count()

    # Debug output
    print(f"DEBUG - All orders: {all_orders_count}, Recent orders: {recent_orders_count}")
    print(f"DEBUG - Current time: {now_time}, Filter cutoff: {filter_time}")

    # Paginate the results
    paginator = Paginator(recent_orders, 10)
    page_number = request.GET.get('page')
    orders_list = paginator.get_page(page_number)

    return render(request, "order_list.html", {
        "orders_list": orders_list,
        "all_orders_count": all_orders_count,
        "recent_orders_count": recent_orders_count,
        "current_time": now_time,
        "filter_time": filter_time,
    })


@login_required(login_url='/user/login/')
def order_transaction_payment(request, order_id):
    order = get_object_or_404(OrderTransaction, id=order_id)

    if request.method == 'POST':
        order.payment_mode = request.POST.get('payment_mode')
        order.transaction_id = request.POST.get('transaction_id')
        order.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)


@login_required(login_url='/user/login/')
def add_order(request):
    unpaid_orders = OrderTransaction.objects.filter(created=today, payment_mode="NO PAYMENT").order_by('-id')
    categories = Category.objects.all()

    if request.method == 'POST':
        form = OrderTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            return redirect('add_order')
    else:
        form = OrderTransactionForm()

    return render(request, 'add_order.html', {
        'form': form,
        'categories': categories,
        'unpaid_orders': unpaid_orders,
    })


@csrf_exempt
@login_required(login_url='/user/login/')
def submit_orders(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        order_id = data.get("random_id")
        orders = data.get("orders", [])
        if not orders:
            return JsonResponse({"error": "No menu items selected"}, status=400)

        order_transaction = OrderTransaction.objects.get(random_id=order_id)
        for order in orders:
            menu_item = MenuItem.objects.get(id=order["menu_item_id"])
            OrderItem.objects.create(
                order=order_transaction,
                menu_item=menu_item,
                customer_name=data.get("customer_name"),
                quantity=order["quantity"],
                status=data.get("status"),
                special_notes=data.get("special_notes"),
                order_type=data.get("order_type")
            )
        return JsonResponse({"message": "Orders placed successfully!", "redirect_url": "/manager/orders_transactions/"})
    except OrderTransaction.DoesNotExist:
        return JsonResponse({"error": "Order transaction not found"}, status=404)
    except MenuItem.DoesNotExist:
        return JsonResponse({"error": "Menu item not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# === ORDER MANAGEMENT ===
@login_required
def getOrder(request, id):
    order = get_object_or_404(OrderItem, id=id)
    settings = Setting.objects.first()
    return render(request, "getorder.html", {"order": order, "setting": settings})


@login_required
def edit_order(request, id):
    order = get_object_or_404(OrderItem, id=id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders')
    else:
        form = OrderForm(instance=order)
    return render(request, 'edit_order.html', {'form': form})


@login_required
def delete_order(request, id):
    order = get_object_or_404(OrderItem, id=id)
    if request.method == 'POST':
        order.delete()
        return redirect('orders')
    return render(request, 'delete_order.html', {'order': order})


@login_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(OrderItem, id=order_id)
    new_status = request.POST.get('status')
    valid_statuses = dict(order._meta.get_field('status').choices)

    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)


# === ORDER TRANSACTIONS ===
@login_required
def orderTransactions(request):
    orders_list = OrderTransaction.objects.filter(payment_mode="NO PAYMENT").order_by('-updated', '-id')
    page = request.GET.get('page')
    orders_page = Paginator(orders_list, 10).get_page(page)
    return render(request, "ordertransactions.html", {"orders_list": orders_page})


@login_required
def clearedTransactions(request):
    orders_list = OrderTransaction.objects.filter(payment_mode__in=["CASH", "MOMO PAY", "AIRTEL PAY"]).order_by('-id')
    page = request.GET.get('page')
    orders_page = Paginator(orders_list, 10).get_page(page)
    return render(request, "cleared_order_transactions.html", {"orders_list": orders_page})


@login_required
def getOrderTransaction(request, id):
    order = get_object_or_404(OrderTransaction, id=id)
    settings = Setting.objects.first()
    order_items = OrderItem.objects.filter(order=order).exclude(status='Cancelled')
    total_price = sum(item.total_price for item in order_items)

    return render(request, "getordertransactions.html", {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'setting': settings
    })


# === REPORTS & CHARTS ===
@login_required
def monthly_order_totals(request):
    data = (
        OrderTransaction.objects
        .annotate(month=TruncMonth('created'))
        .values('month')
        .annotate(total_orders=Count('id'))
        .order_by('month')
    )

    return JsonResponse({
        'months': [item['month'].strftime('%b') for item in data],
        'totals': [item['total_orders'] for item in data]
    })


@login_required
def pos_reports(request):
    return render(request, "reports.html", {})

