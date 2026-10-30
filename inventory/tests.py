import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, MenuItem, OrderItem, OrderTransaction


class OrderPriceOverrideTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="counter-staff",
            password="test-password",
        )
        self.client.force_login(self.user)
        category = Category.objects.create(
            name="Main Dishes",
            description="Main dishes",
            grouping="Main Dishes",
        )
        self.menu_item = MenuItem.objects.create(
            category=category,
            name="Test meal",
            description="Test meal description",
            price=Decimal("10000.00"),
        )

    def test_submit_order_saves_override_and_uses_it_for_total(self):
        response = self.client.post(
            reverse("submit_orders"),
            data=json.dumps({
                "orders": [{
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 2,
                    "unit_price": "8500.50",
                }],
                "order_type": "Dine-In",
                "special_notes": "nothing",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        order_transaction = OrderTransaction.objects.get(
            random_id=response.json()["random_id"]
        )
        order_item = OrderItem.objects.get(order=order_transaction)
        self.assertEqual(order_item.unit_price, Decimal("8500.50"))
        self.assertEqual(order_item.total_price, Decimal("17001.00"))
        self.menu_item.refresh_from_db()
        self.assertEqual(self.menu_item.price, Decimal("10000.00"))

    def test_unavailable_item_rejects_order_before_creating_ticket(self):
        self.menu_item.is_available = False
        self.menu_item.save(update_fields=["is_available"])

        response = self.client.post(
            reverse("submit_orders"),
            data=json.dumps({
                "orders": [{
                    "menu_item_id": self.menu_item.pk,
                    "quantity": 1,
                    "unit_price": "8500.50",
                }],
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(OrderTransaction.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
