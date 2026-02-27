from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Booking
import logging

logger = logging.getLogger(__name__)


def update_booking_statuses():
    now = timezone.now()
    updated_count = 0

    # faqat kerakli statusdagi bookinglarni olamiz
    bookings = Booking.objects.filter(
        status__in=["pending", "in_progress"]
    ).select_related('user', 'service')

    for booking in bookings:
        try:
            old_status = booking.status
            booking.update_status_based_on_time()

            if booking.status != old_status:
                booking.save(update_fields=["status"])
                updated_count += 1
                logger.info(f"Booking #{booking.id} statusi {old_status} → {booking.status} ga o'zgartirildi")

        except Exception as e:
            logger.error(f"Booking #{booking.id} statusini yangilashda xato: {str(e)}", exc_info=True)
            # yoki continue qilib qolganlarini davom ettirish mumkin

    logger.info(f"Jami {updated_count} ta booking statusi yangilandi")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())

    # Har 5 daqiqada ishlaydi
    scheduler.add_job(
        update_booking_statuses,
        'interval',
        minutes=5,
        id='update_booking_statuses',      # unique ID (keyin to'xtatish/o'zgartirish uchun)
        replace_existing=True               # agar allaqachon bo'lsa, yangisini almashtiradi
    )

    try:
        scheduler.start()
        logger.info("Booking status scheduler ishga tushdi (har 5 daqiqada)")
    except Exception as e:
        logger.error(f"Scheduler ishga tushmadi: {e}")