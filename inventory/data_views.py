from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Category, MenuItem, DiningArea, Table
from django.db.models import Sum, Count
from .data_forms import CategoryForm, MenuItemForm, DiningAreaForm, TableForm


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


# ----- CATEGORY VIEWS -----
class CategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = 'data/category_list.html'
    paginate_by = 10
    queryset = Category.objects.annotate(
        items_count=Count('menu_items')
    )

    
class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'data/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'data/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'data/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')


# ----- MENU ITEM VIEWS -----
class MenuItemListView(StaffRequiredMixin, ListView):
    model = MenuItem
    template_name = 'data/menuitem_list.html'


class MenuItemCreateView(StaffRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'data/menuitem_form.html'
    success_url = "/data/menu-items/"


class MenuItemUpdateView(StaffRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'data/menuitem_form.html'
    success_url = "/data/menu-items/"


class MenuItemDeleteView(StaffRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'data/menuitem_confirm_delete.html'
    success_url = "/data/menu-items/"


# ----- DINING AREA VIEWS -----
class DiningAreaListView(StaffRequiredMixin, ListView):
    model = DiningArea
    template_name = 'data/diningarea_list.html'
    context_object_name = 'dining_areas'
    
    def get_queryset(self):
        return DiningArea.objects.prefetch_related('tables').all()
    
    
class DiningAreaCreateView(StaffRequiredMixin, CreateView):
    model = DiningArea
    form_class = DiningAreaForm
    template_name = 'data/diningarea_form.html'
    success_url = '/data/dining-areas/'


class DiningAreaUpdateView(StaffRequiredMixin, UpdateView):
    model = DiningArea
    form_class = DiningAreaForm
    template_name = 'data/diningarea_form.html'
    success_url = '/data/dining-areas/'


class DiningAreaDeleteView(StaffRequiredMixin, DeleteView):
    model = DiningArea
    template_name = 'data/diningarea_confirm_delete.html'
    success_url = '/data/dining-areas/'


# ----- TABLE VIEWS -----
class TableListView(StaffRequiredMixin, ListView):
    model = Table
    template_name = 'data/table_list.html'


class TableCreateView(StaffRequiredMixin, CreateView):
    model = Table
    form_class = TableForm
    template_name = 'data/table_form.html'
    success_url = '/data/dining-areas/'


class TableUpdateView(StaffRequiredMixin, UpdateView):
    model = Table
    form_class = TableForm
    template_name = 'data/table_form.html'
    success_url = '/data/dining-areas/'

class TableDeleteView(StaffRequiredMixin, DeleteView):
    model = Table
    template_name = 'data/table_confirm_delete.html'
    success_url = '/data/dining-areas/'
