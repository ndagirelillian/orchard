from django.apps import AppConfig


class RoomBookingsConfig(AppConfig):
  
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'room_bookings'

    def ready(self):
        import room_bookings.signals