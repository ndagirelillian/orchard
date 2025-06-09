from django import forms
from .models import Staff, StaffAttendance
from django.utils import timezone

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'
        exclude = ["is_active"]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
        

class StaffAttendanceForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = ['staff', 'date', 'time_in', 'status', 'remarks']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StaffCheckoutForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = ['time_out', 'date_out']
        widgets = {
            'time_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'readonly': 'readonly'}),
            'date_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': 'readonly'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.time_out = timezone.now().time()
        instance.date_out = timezone.now().date()
        if commit:
            instance.save()
        return instance
    
    
class EditStaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'
  
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active':forms.Select(attrs={'class':'form-control'})
        }
