from django.apps import AppConfig
import os

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'

    def ready(self):

        if os.environ.get('RUN_MAIN', None) != 'true':
            return


        from .scheduler import start_scheduler
        start_scheduler()