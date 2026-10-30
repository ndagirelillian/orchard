from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .forms import RoomReservationForm
from .models import Room, RoomReservation, RoomType


class ReservationPriceOverrideTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reception")
        room_type = RoomType.objects.create(
            name="Standard",
            base_price=Decimal("100000.00"),
        )
        self.room = Room.objects.create(
            room_number="101",
            room_type=room_type,
            capacity=2,
            price_per_night=100000,
            floor=1,
        )

    def test_staff_override_is_saved_and_used_for_total(self):
        check_in = timezone.localdate() + timedelta(days=5)
        form = RoomReservationForm(data={
            "room": self.room.pk,
            "customer": "Test Guest",
            "email": "guest@example.com",
            "phone_number": "+256771234567",
            "NIN": "TEST-123",
            "check_in_date": check_in.isoformat(),
            "check_out_date": (check_in + timedelta(days=2)).isoformat(),
            "booked_price_per_night": "85000.50",
            "special_requests": "",
        })

        self.assertTrue(form.is_valid(), form.errors)
        reservation = form.save(commit=False)
        reservation.created_by = self.user
        reservation.save()

        self.assertEqual(reservation.booked_price_per_night, Decimal("85000.50"))
        self.assertEqual(reservation.total_price, Decimal("170001.00"))
        self.room.refresh_from_db()
        self.assertEqual(self.room.price_per_night, 100000)
