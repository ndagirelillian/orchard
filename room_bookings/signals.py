# bookings/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, RoomReservation
from django.utils import timezone


@receiver(post_save, sender=Booking)
def create_reservation_on_status_change(sender, instance, created, **kwargs):
    if instance.status == 'reserved' and not hasattr(instance, 'reservation'):
        RoomReservation.objects.create(
            booking=instance,
            room=instance.room,
            customer=f"{instance.first_name} {instance.last_name}",
            email=instance.email,
            phone_number=instance.contact,
            check_in_date=instance.check_in,
            check_out_date=instance.check_out,
            reservation_date=timezone.now(),
            status='Confirmed',
            special_requests=instance.special_requests
        )
