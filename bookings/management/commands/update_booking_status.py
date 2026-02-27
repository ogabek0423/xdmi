from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking


class Command(BaseCommand):
    help = "Update booking statuses based on current time"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        updated_count = 0

        bookings = Booking.objects.all()

        for booking in bookings:
            old_status = booking.status
            booking.update_status_based_on_time()
            if booking.status != old_status:
                booking.save(update_fields=["status"])
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"{updated_count} booking status updated.")
        )