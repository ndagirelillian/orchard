from django.urls import path

from inventory.generate_csv_reports.order_csv_report import export_orders_to_csv
from . import views
from inventory.generate_pdfs.create_invoice import print_order_invoice
from inventory.generate_pdfs.create_order import print_order
from inventory.generate_pdfs.create_order_transactions import print_order_receipt
# from inventory.generate_csv_reports.order_csv_report import export_orders_to_csv
from inventory.generate_csv_reports.paid_order_csv import export_paid_order_to_csv
from inventory.generate_csv_reports.general_order_csv import export_general_order_to_csv, export_orders_report
from inventory.generate_csv_reports.order_csv_report import export_orders_to_csv, export_reservations_to_csv
urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Categories and Menu
   
    path('load-menu-items/', views.load_menu_items, name='load_menu_items'),

    # Orders
    path('orders/', views.orders, name='order_list'),
    path('add-order/', views.add_order, name='add_order'),
    path("submit-orders/", views.submit_orders, name="submit_orders"),
    path('order/edit/<int:id>/', views.edit_order_item, name='edit_order'),
    path('orders/<str:id>/', views.getOrder, name='get_order'),
    path('print_order/<int:id>/', print_order, name='print_order'),
    path('print_receipt/<int:order_id>/', print_order_receipt, name='print_order_receipt'),
    path('print_invoice/<int:order_id>/', print_order_invoice, name='print_order_invoice'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),

    # Order Transactions
    path('orders_transactions/', views.orderTransactions, name='order_transactions'),
    path('cleared_transactions/', views.clearedTransactions, name='cleared_transactions'),
    path('orders_transactions/<str:id>/', views.getOrderTransaction, name='get_orderTransaction'),
    path('ordertransaction/<int:order_id>/payment/', views.order_transaction_payment, name='order_payment'),
    
    # Totals
    path('monthly-order-totals/', views.monthly_order_totals, name='monthly_order_totals'),
    
    # Reports
    path('reports/', views.pos_reports, name="pos_reports"),
    path('export-orders/<str:time_period>/',
         export_orders_to_csv, name='export_orders'),
    path('export_csv/reservations/<str:time_period>/',
         export_reservations_to_csv, name='export_reservations'),
    
    # path('export-orders/', export_orders_to_csv, name='export_order_items'),
    path('paid-orders/', export_paid_order_to_csv, name='paid-orders'),
    path('general-orders/', export_general_order_to_csv, name='general_orders'),
    path('orders-transactions/csv/', export_orders_report, name='orders_report'),
    

    path("search-menu-items/", views.search_menu_items, name="search_menu_items"),
  

]
