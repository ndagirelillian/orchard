from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import random

class RoomType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    room_image = models.ImageField(upload_to="rooms", blank=True, null=True)

    def __str__(self):
        return self.name

class HotelBranch(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    hotel = models.ForeignKey(HotelBranch, on_delete=models.CASCADE, related_name='rooms', blank=True, null=True)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    price_per_night = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    room_image = models.ImageField(upload_to="rooms", blank=True, null=True)
    floor = models.IntegerField()

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"
    
    def check_availability(self, check_in_date, check_out_date, exclude_reservation=None):
        """
        Check if the room is available for the given date range.
        Returns True if available, False otherwise.
        """
        # Query for overlapping reservations
        overlapping_reservations = RoomReservation.objects.filter(
            room=self,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            status__in=['Pending', 'Confirmed', 'Checked-In']
        )
        
        # If we're updating an existing reservation, exclude it from the check
        if exclude_reservation:
            overlapping_reservations = overlapping_reservations.exclude(id=exclude_reservation.id)
            
        return not overlapping_reservations.exists()
    
    def update_availability_status(self):
        """
        Update the room's availability status based on current reservations.
        """
        today = timezone.now().date()
        active_reservations = RoomReservation.objects.filter(
            room=self,
            check_in_date__lte=today,
            check_out_date__gte=today,
            status__in=['Confirmed', 'Checked-In']
        ).exists()
        
        self.is_available = not active_reservations
        self.save(update_fields=['is_available'])

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    NIN = models.CharField(max_length=100, default="")
    customerid_image = models.ImageField(upload_to="rooms", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class RoomReservation(models.Model):
    RESERVATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Checked-In', 'Checked-In'),
        ('Checked-Out', 'Checked-Out'),
    ]

    reservation_id = models.BigIntegerField(unique=True, editable=False, default=0)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    customer = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    NIN = models.CharField(max_length=100, default="")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    reservation_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=RESERVATION_STATUS_CHOICES, default='Pending')
    special_requests = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)

    def __str__(self):
        return f"Reservation for {self.customer} - Room {self.room.room_number}"

    @property
    def total_nights(self):
        return (self.check_out_date - self.check_in_date).days

    @property
    def is_active(self):
        return self.check_in_date <= timezone.now().date() <= self.check_out_date

    def calculate_total_price(self):
        if self.room.price_per_night and self.total_nights > 0:
            return self.total_nights * self.room.price_per_night
        return 0

    def clean(self):
        # Ensure check-in date is not in the past
        if self.check_in_date < timezone.now().date():
            raise ValidationError("Check-in date cannot be in the past.")

        # Ensure checkout date is after check-in date
        if self.check_out_date <= self.check_in_date:
            raise ValidationError("Checkout date must be after the check-in date.")
            
        # Check if the room is available for the selected dates
        # Skip this check if the reservation is being cancelled or checked-out
        if self.status not in ['Cancelled', 'Checked-Out']:
            # When updating a reservation, pass the current reservation to exclude it from the check
            is_available = self.room.check_availability(
                self.check_in_date, 
                self.check_out_date,
                exclude_reservation=self if self.pk else None
            )
            
            if not is_available:
                raise ValidationError(f"Room {self.room.room_number} is not available for the selected dates.")

    def save(self, *args, **kwargs):
        # Assign a unique 9-digit reservation ID if not set
        if not self.reservation_id or self.reservation_id < 100000000:
            self.reservation_id = random.randint(100000000, 999999999)

        # Calculate total price
        self.total_price = self.calculate_total_price()

        # Get the previous status if this is an existing reservation
        old_status = None
        if self.pk:
            old_instance = RoomReservation.objects.get(pk=self.pk)
            old_status = old_instance.status

        # Run validation before saving
        self.clean()
        
        # Save the reservation
        super().save(*args, **kwargs)
        
        # If status has changed or this is a new reservation, update room availability
        if old_status != self.status or old_status is None:
            self.room.update_availability_status()

#SAUNA
class Sauna_services(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class SaunaUser(models.Model):
    KEY_CHOICES = [
    (f"key_{str(i).zfill(3)}", f"key_{str(i).zfill(3)}") for i in range(1, 17)
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    customer_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    service = models.ForeignKey(Sauna_services, on_delete=models.CASCADE)
    keys = models.CharField(max_length=100, choices=KEY_CHOICES)
    price = models.IntegerField(blank=True, null=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.service:
            self.price = self.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer_name