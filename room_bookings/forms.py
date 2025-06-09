from django import forms
from .models import Customer, SaunaUser, RoomReservation
from django.core.validators import RegexValidator
from django.utils import timezone
from django import forms
from .models import RoomType, Room

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'NIN'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'NIN': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SaunaUserForm(forms.ModelForm):
    class Meta:
        model = SaunaUser
        fields = [
            'customer_name',
            'gender',
            'service',
            'keys'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'keys': forms.Select(attrs={'class': 'form-control'}),
        }


class RoomReservationForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone_number = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890',
            'pattern': '^\+?[0-9]{9,15}$'
        })
    )
    
    NIN = forms.CharField(
        label="National ID Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your government-issued ID'
        })
    )

    class Meta:
        model = RoomReservation
        fields = [
            'room', 
            'customer',
            'email',
            'phone_number',
            'NIN',
            'check_in_date', 
            'check_out_date', 
            'special_requests'
        ]
        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-select',
                'data-bind': 'room-select'
            }),
            'customer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com'
            }),
            'check_in_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'check_out_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or notes...'
            }),
        }
        labels = {
            'room': 'Select Room',
            'customer': 'Full Name',
            'check_in_date': 'Check-in Date',
            'check_out_date': 'Check-out Date'
        }
        help_texts = {
            'NIN': 'Government-issued identification number',
            'special_requests': 'Please mention any accessibility needs or preferences'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initially restrict to rooms that are marked as available
        self.fields['room'].queryset = Room.objects.filter(is_available=True)

        # Optionally, dynamically filter further once check-in/out are entered (for AJAX or custom views)
        if 'check_in_date' in self.data and 'check_out_date' in self.data:
            try:
                check_in = self.data.get('check_in_date')
                check_out = self.data.get('check_out_date')
                if check_in and check_out:
                    available_rooms = []
                    for room in Room.objects.all():
                        if room.check_availability(check_in, check_out):
                            available_rooms.append(room.id)
                    self.fields['room'].queryset = Room.objects.filter(id__in=available_rooms)
            except Exception:
                pass  # fallback to initial is_available=True

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')

        if check_in and check_out:
            if check_in < timezone.now().date():
                raise forms.ValidationError("Check-in date cannot be in the past")
            if check_out <= check_in:
                raise forms.ValidationError("Check-out date must be after check-in date")
        return cleaned_data


class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'room_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'room_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['hotel']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'room_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        
class ReservationStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = RoomReservation
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
