from django.urls import path
from . import views

urlpatterns = [
    path('financial-report/', views.financial_report, name='finances'),
    path('revenue/add/', views.add_revenue, name='add_revenue'),
    path('expense/add/', views.add_expense, name='add_expense'),
    path('asset/add/', views.add_asset, name='add_asset'),
    path('liability/add/', views.add_liability, name='add_liability'),
    
    
    #lists
    path('all-assets/', views.all_assets, name='assets'),
    path('all-liabilities/', views.liabities, name='liabilities'),
    path('all-revenue/', views.revenue, name='revenue'),
    path('all-expense/', views.expense, name='expense'),
    path('asset-detail/<int:id>/', views.asset_detail, name='asset_detail'),
    path('register-depreciation/', views.register_depreciation,
         name='register_depreciation'),
    path('budget-report/', views.budget_report, name='budget_report'),

    
]
