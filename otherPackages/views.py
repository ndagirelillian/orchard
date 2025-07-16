from datetime import timezone
from django.views.generic import CreateView, ListView

from finance.models import Revenue
from .models import OtherPackage
from .forms import OtherPackageForm
import csv
from django.http import HttpResponse
from django.views.generic import UpdateView
from django.utils import timezone



class PackageCreateView(CreateView):
    model = OtherPackage
    form_class = OtherPackageForm
    template_name = 'package_form.html'
    success_url = '/others/packages/'

    def get_form_kwargs(self):
        """Remove 'created_by' from the form kwargs if present"""
        kwargs = super().get_form_kwargs()
        kwargs.pop('created_by', None)
        return kwargs

    def form_valid(self, form):
        """Set the created_by field and calculate balance before saving"""
        if form.is_valid():
            package = form.save(commit=False)
            package.created_by = self.request.user

            # Calculate the balance
            package.balance = package.total_amount - package.amount_paid

            package.save()
            return super().form_valid(form)
    

class PackageListView(ListView):
    model = OtherPackage
    template_name = 'package_list.html'
    context_object_name = 'packages'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs
    
    
class PackageUpdateView(UpdateView):
    model = OtherPackage
    form_class = OtherPackageForm
    template_name = 'package_form.html'
    success_url = '/others/packages/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('created_by', None)
        return kwargs

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.old_amount_paid = self.object.amount_paid  # store old value
        return self.object

    def form_valid(self, form):
        instance = form.save(commit=False)
        new_amount_paid = form.cleaned_data['amount_paid']
        amount_difference = new_amount_paid - self.old_amount_paid

        if amount_difference > 0:
            # Update balance
            instance.balance = instance.total_amount - new_amount_paid
            instance.save()

            # Add new revenue entry for the added amount
            Revenue.objects.create(
                category='other',
                description=f"{instance.get_service_type_display()} - {instance.client_name} - {instance.id} - Payment Update",
                amount=amount_difference,
                received_from=instance.client_name,
                date=timezone.now().date(),
                created_by=instance.created_by,
            )

        return super().form_valid(form)


def export_packages_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="service_packages.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Client Name', 'Service Type', 'Start Time', 'End Time', 
        'Duration (hrs)', 'Total Amount', 'Status', 'Created By'
    ])

    packages = OtherPackage.objects.select_related('created_by').all()
    
    for pkg in packages:
        writer.writerow([
            pkg.client_name,
            pkg.get_service_type_display(),
            pkg.start_time.strftime("%Y-%m-%d %H:%M"),
            pkg.end_time.strftime("%Y-%m-%d %H:%M"),
            pkg.duration,
            pkg.total_amount,
            pkg.status,
            pkg.created_by.username if pkg.created_by else 'System'
        ])

    return response