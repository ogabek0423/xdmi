from django.apps import AppConfig
import os

class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'           # app nomingiz

    def ready(self):
        # ready() ikki marta ishga tushishi oldini olish uchun (runserver + autoreload)
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        # faqat asosiy jarayonda scheduler ishga tushadi
        from .scheduler import start_scheduler
        start_scheduler()