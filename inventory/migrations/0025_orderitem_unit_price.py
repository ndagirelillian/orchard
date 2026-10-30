from decimal import Decimal

from django.db import migrations, models


def populate_unit_prices(apps, schema_editor):
    OrderItem = apps.get_model("inventory", "OrderItem")
    batch = []
    for order_item in OrderItem.objects.select_related("menu_item").iterator():
        if order_item.menu_item_id:
            order_item.unit_price = order_item.menu_item.price
        else:
            order_item.unit_price = Decimal("0.00")
        batch.append(order_item)
        if len(batch) == 500:
            OrderItem.objects.bulk_update(batch, ["unit_price"])
            batch.clear()
    if batch:
        OrderItem.objects.bulk_update(batch, ["unit_price"])


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0024_alter_ordertransaction_payment_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="unit_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.RunPython(populate_unit_prices, migrations.RunPython.noop),
    ]
