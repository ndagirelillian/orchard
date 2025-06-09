from django import forms
from .models import OrderTransaction, OrderItem, MenuItem, Category, Table
from django.utils.timezone import localdate


class OrderForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'category-select'})
    )
    menu_item = forms.ModelChoiceField(
        queryset=MenuItem.objects.none(),
        label="Menu Item",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'menu-item-select'})
    )

    class Meta:
        model = OrderItem
        fields = [
            'order',
            'category',
            'menu_item',
            'customer_name',
            'quantity',
            'status',
            'special_notes',
            'order_type',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'special_notes': forms.Select(attrs={'class': 'form-control'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = localdate()
        self.fields['order'].queryset = OrderTransaction.objects.filter(created=today).order_by('-id')

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['menu_item'].queryset = MenuItem.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                self.fields['menu_item'].queryset = MenuItem.objects.none()
        elif self.instance.pk and self.instance.menu_item:
            self.fields['category'].initial = self.instance.menu_item.category
            self.fields['menu_item'].queryset = MenuItem.objects.filter(category=self.instance.menu_item.category)


class OrderTransactionForm(forms.ModelForm):

    class Meta:
        model = OrderTransaction
        fields = ['customer_name', 'served_by','table']
        widgets = {

            
            'table': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'served_by':forms.TextInput(attrs={'class':'form-control'})
        }


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = [
            'order',
            'menu_item',
            'customer_name',
            'quantity',
            'status',
            'order_type',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'menu_item': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load all menu items in the dropdown by default
        self.fields['menu_item'].queryset = MenuItem.objects.all()


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class OrderTransactionPaymentForm(forms.ModelForm):
    class Meta:
        model = OrderTransaction
        fields = ['payment_mode', 'transaction_id']
        widgets = {
            'payment_mode': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave Blank if Cash Payment'
            }),
        }
