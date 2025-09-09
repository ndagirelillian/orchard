from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Revenue
from django.utils import timezone
from decimal import Decimal
from inventory.models import OrderTransaction
from room_bookings.models import RoomReservation, Sauna_services, SaunaUser
from otherPackages.models import OtherPackage

from django.db.models.signals import pre_save, post_save

# Temporary storage to track changes
_previous_payment_modes = {}


@receiver(pre_save, sender=OrderTransaction)
def track_previous_payment_mode(sender, instance, **kwargs):
    if instance.pk:
        old_instance = OrderTransaction.objects.get(pk=instance.pk)
        _previous_payment_modes[instance.pk] = old_instance.payment_mode


@receiver(post_save, sender=OrderTransaction)
def create_revenue_from_order(sender, instance, created, **kwargs):
    excluded_modes = ["NO PAYMENT", "ON ACCOMMODATION", "INVOICE"]
    allowed_modes = ["CASH", "MOMO PAY", "AIRTEL PAY"]

    if created:
        return  # Don't act on creation because it's always "NO PAYMENT"

    previous_mode = _previous_payment_modes.get(instance.pk)

    # Only trigger if payment_mode changed and new mode is allowed
    if previous_mode != instance.payment_mode and instance.payment_mode in allowed_modes:
        if not Revenue.objects.filter(description__icontains=f"Order {instance.random_id}").exists():
            total_amount = sum(
                item.total_price for item in instance.order_items.all())

            Revenue.objects.create(
                category='fnb',
                description=f"F&B Payment for Order {instance.random_id}",
                amount=Decimal(total_amount),
                received_from=instance.customer_name or "walk-in",
                date=timezone.now().date(),
                created_by=instance.created_by,
            )

    # Clean up
    _previous_payment_modes.pop(instance.pk, None)



# @receiver(post_save, sender=OrderTransaction)
# def create_revenue_from_order(sender, instance, created, **kwargs):
#     if created and instance.payment_mode not in ["NO PAYMENT", "ON ACCOMMODATION", "INVOICES"]:
#         # Prevent duplicates: only create if no existing revenue for this order
#         if not Revenue.objects.filter(description__icontains=f"Order {instance.random_id}").exists():
#             total_amount = sum(
#                 item.total_price for item in instance.order_items.all())

#             Revenue.objects.create(
#                 category='fnb',
#                 description=f"F&B Payment for Order {instance.random_id}",
#                 amount=Decimal(total_amount),
#                 received_from=instance.customer_name or "walk-in",
#                 date=timezone.now().date(),
#                 created_by=instance.created_by,
#             )
@receiver(post_save, sender=RoomReservation)
def add_revenue_on_check_in(sender, instance, created, **kwargs):
    if instance.status != "Pending" and instance.status != "Cancelled":
        # Prevent duplicate revenue entries
        description = f"Room {instance.room.room_number} check-in - {instance.reservation_id}"
        if not Revenue.objects.filter(description=description).exists():
            Revenue.objects.create(
                category='rooms',
                description=description,
                amount=instance.total_price,
                received_from=instance.customer or "Guest",
                date=timezone.now().date(),
                created_by=instance.created_by,
            )


# Temporarily store old value
@receiver(pre_save, sender=SaunaUser)
def store_previous_payment_mode(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = SaunaUser.objects.get(pk=instance.pk)
            instance._old_payment_mode = previous.payment_mode
        except SaunaUser.DoesNotExist:
            instance._old_payment_mode = None


@receiver(post_save, sender=SaunaUser)
def add_revenue_on_sauna_payment(sender, instance, created, **kwargs):
    """
    Signal to create Revenue when SaunaUser pays,
    excluding 'NO PAYMENT' and 'ON_ACCOMMODATION'.
    Also works when payment_mode changes from a non-paying mode to a paying mode.
    """
    non_payment_modes = ["NO PAYMENT", "ON ACCOMMODATION"]

    # When newly created and is a paying mode
    if created and instance.payment_mode not in non_payment_modes:
        Revenue.objects.create(
            category='sauna',
            description=f"Sauna Service: {instance.service.name} for {instance.customer_name}",
            amount=instance.price or instance.service.price,
            received_from=instance.customer_name,
            date=instance.order_date.date() if instance.order_date else timezone.now().date(),
            created_by=instance.created_by,
        )

    # When payment_mode was changed from non-payment to a paying mode
    elif not created:
        old_mode = getattr(instance, "_old_payment_mode", None)
        if old_mode in non_payment_modes and instance.payment_mode not in non_payment_modes:
            Revenue.objects.create(
                category='sauna',
                description=f"Sauna Service (Updated): {instance.service.name} for {instance.customer_name}",
                amount=instance.price or instance.service.price,
                received_from=instance.customer_name,
                date=instance.order_date.date() if instance.order_date else timezone.now().date(),
                created_by=instance.created_by,
            )


@receiver(post_save, sender=OtherPackage)
def add_revenue_on_service_completion(sender, instance, created, **kwargs):
    if created:
        description = f"{instance.get_service_type_display()} - {instance.client_name} - {instance.id} - Initial Payment"
        Revenue.objects.create(
            category='other',
            description=description,
            amount=instance.amount_paid,
            received_from=instance.client_name,
            date=timezone.now().date(),
            created_by=instance.created_by,
        )
