from django.shortcuts import render
from inventory.models import *
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import date
from django.db.models import Prefetch


def kitchen(request):
    active_statuses = ("Pending", "Preparing", "Cooked")
    tickets = (
        OrderTransaction.objects
        .filter(order_items__status__in=active_statuses)
        .distinct()
        .prefetch_related(
            Prefetch(
                "order_items",
                queryset=OrderItem.objects.filter(
                    status__in=active_statuses,
                ).select_related("menu_item").order_by("id"),
                to_attr="kitchen_items",
            )
        )
        .order_by("created", "id")
    )
    template = "kitchen/_tickets.html" if request.GET.get("partial") == "1" else "kitchen.html"
    return render(request, template, {
        "tickets": tickets,
        "status_choices": OrderItem._meta.get_field("status").choices,
    })


@require_POST
def update_order_status(request, order_id):
    """
    Updates the status of a specific order item.
    """
    order = get_object_or_404(OrderItem, id=order_id)
    new_status = request.POST.get('status')

    # Validate the status to match available choices in the model
    valid_statuses = dict(OrderItem._meta.get_field('status').choices)
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        messages.success(
            request, f"Order {order.id} status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect('kitchen')
