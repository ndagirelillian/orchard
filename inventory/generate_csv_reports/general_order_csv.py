import csv
from django.http import HttpResponse
from inventory.models import OrderItem, OrderTransaction
from django.http import HttpResponse
import csv
from django.utils import timezone
from decimal import Decimal

def  export_general_order_to_csv(request):
    # Create the HttpResponse object with content type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="order_items_report.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write the headers to the CSV file
    writer.writerow([
        'Order ID', 'Menu Item', 'Customer Name', 'Table', 'Dining Area', 'Quantity', 
        'Total Price', 'Status', 'Order Type', 'Special Notes','Mode of Payment', 'Transaction ID', 'Order Date'
    ])

    # Fetch all OrderItem records (you can add filters if needed)
    order_items = OrderItem.objects.all().select_related('menu_item', 'order', 'table', 'dining_area')

    # Write the data rows
    for item in order_items:
        writer.writerow([
            item.order.random_id,
            item.menu_item.name if item.menu_item else 'N/A',
            item.customer_name,
            item.table.table_number if item.table else 'N/A',
            item.dining_area.name if item.dining_area else 'N/A', 
            item.quantity,
            item.total_price,
            item.status, 
            item.order_type, 
            item.special_notes if item.special_notes else 'N/A',
            item.order.payment_mode,
            item.order.transaction_id,
            item.order_date.strftime('%Y-%m-%d'), 
        ])

    return response


def export_orders_report(request):
    response = HttpResponse(content_type='text/csv')
    filename = f"orders_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    
    # Updated CSV headers for grouped transactions
    writer.writerow([
        'Transaction ID', 'Customer Name', 'Dining Area', 'Table Number',
        'Payment Mode', 'Transaction Date', 'Created By', 'Total Quantity',
        'Transaction Total', 'Order Items', 'Special Notes', 'Order Types',
        'Item Statuses', 'Last Updated'
    ])

    transactions = OrderTransaction.objects.prefetch_related('order_items').all()

    for transaction in transactions:
        items = transaction.order_items.all()
        item_details = []
        total_quantity = 0
        transaction_total = Decimal('0.00')
        statuses = set()
        order_types = set()
        special_notes = set()

        for item in items:
            # Build item description
            item_desc = []
            if item.menu_item:
                item_desc.append(f"{item.menu_item.name}")
            if item.quantity:
                item_desc.append(f"Qty: {item.quantity}")
                total_quantity += item.quantity
            if item.total_price:
                item_desc.append(f"Price: {item.total_price:.2f}")
                transaction_total += item.total_price
            if item.special_notes != 'nothing':
                item_desc.append(f"Notes: {item.special_notes}")
            
            item_details.append(" | ".join(item_desc))
            statuses.add(item.status)
            order_types.add(item.order_type)
            if item.special_notes != 'nothing':
                special_notes.add(item.special_notes)

        # Format aggregated values
        order_items = "\n".join(item_details) or "No items"
        statuses = ", ".join(sorted(statuses)) or "N/A"
        order_types = ", ".join(sorted(order_types)) or "N/A"
        special_notes = ", ".join(sorted(special_notes)) or "No special notes"

        writer.writerow([
            transaction.random_id,
            transaction.customer_name or "N/A",
            transaction.dining_area.name if transaction.dining_area else "N/A",
            transaction.table.table_number if transaction.table else "N/A",
            transaction.payment_mode,
            transaction.created.strftime("%Y-%m-%d %H:%M"),
            transaction.created_by.username if transaction.created_by else "System",
            total_quantity,
            f"{transaction_total:.2f}",
            order_items,
            special_notes,
            order_types,
            statuses,
            transaction.updated.strftime("%Y-%m-%d %H:%M") if transaction.updated else "N/A"
        ])

    return response