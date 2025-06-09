# forms.py
from django import forms
from .models import Category, MenuItem, DiningArea, Table
from decimal import Decimal

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'grouping', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'grouping': forms.Select(attrs={'class': 'form-select'}),
            'image_url': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'price', 'is_available', 'image_url']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image_url': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class DiningAreaForm(forms.ModelForm):
    class Meta:
        model = DiningArea
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
        }

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['dining_area', 'table_number', 'capacity', 'is_available']
        widgets = {
            'dining_area': forms.Select(attrs={'class': 'form-select'}),
            'table_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }