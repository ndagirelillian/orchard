from django.db import migrations, models


def populate_booked_rates(apps, schema_editor):
    RoomReservation = apps.get_model("room_bookings", "RoomReservation")
    batch = []
    for reservation in RoomReservation.objects.select_related("room").iterator():
        reservation.booked_price_per_night = (
            reservation.room.price_per_night or 0
        )
        batch.append(reservation)
        if len(batch) == 500:
            RoomReservation.objects.bulk_update(
                batch, ["booked_price_per_night"]
            )
            batch.clear()
    if batch:
        RoomReservation.objects.bulk_update(
            batch, ["booked_price_per_night"]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("room_bookings", "0003_alter_saunauser_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="roomreservation",
            name="booked_price_per_night",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.RunPython(populate_booked_rates, migrations.RunPython.noop),
    ]
