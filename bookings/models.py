from facilities.models import Service
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("not_attended", "Not Attended"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    people_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["service", "start_time", "end_time", "status"]),
            models.Index(fields=["user", "start_time", "status"]),
        ]
    def __str__(self):
        return f"{self.user.email} — {self.service.name} ({self.start_time.date()})"

    # ================== Validation ==================
    def clean(self):
        now = timezone.now()

        if not self.pk:  # agar yangi bo‘lsa
            if self.user.blocked_until and self.user.blocked_until > now:
                raise ValidationError(
                    f"Siz bloklangansiz. Bron qila olmaysiz. Blok muddati: {self.user.blocked_until.strftime('%Y-%m-%d %H:%M')} gacha")

        if not self.pk:
            if self.start_time < now:
                raise ValidationError("O‘tmishdagi vaqtga bron qilib bo‘lmaydi.")
            if self.start_time > now + timedelta(days=90):
                raise ValidationError("3 oydan uzoq vaqtga bron qilish mumkin emas.")

        if self.start_time >= self.end_time:
            raise ValidationError("Tugash vaqti boshlanish vaqtidan keyin bo‘lishi kerak.")

        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        if duration_hours < 0.5:
            raise ValidationError("Minimal bron vaqti 30 daqiqa bo‘lishi kerak.")

        # Exclusive tekshiruvi
        if self.service.is_exclusive:
            conflict = Booking.objects.filter(
                service=self.service,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                status__in=["pending", "in_progress"]
            ).exclude(pk=self.pk)
            if conflict.exists():
                raise ValidationError("Bu xizmat ushbu vaqtda band (exclusive). Boshqa vaqt tanlang.")

        # Capacity tekshiruvi
        else:
            overlapping = Booking.objects.filter(
                service=self.service,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                status__in=["pending", "in_progress"]
            ).exclude(pk=self.pk)
            current_total = sum(b.people_count for b in overlapping)
            if current_total + self.people_count > self.service.capacity:
                raise ValidationError(
                    f"Sig‘imdan oshib ketdi! Mavjud: {current_total} kishi, qo‘shilmoqda: {self.people_count}, "
                    f"Limit: {self.service.capacity} kishi"
                )

        # Bir vaqtda bir facilityda bo‘lish
        overlapping_user = Booking.objects.filter(
            user=self.user,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=["pending", "in_progress"]
        ).exclude(pk=self.pk)
        if overlapping_user.filter(~Q(service__facility=self.service.facility)).exists():
            raise ValidationError("Bir vaqtning o‘zida faqat bitta sport zalida bo‘lish mumkin.")

    # ================== Save ==================
    def save(self, *args, **kwargs):
        self.full_clean()

        # duration_hours ni Decimal qilish (xavfsizlik uchun)
        duration_seconds = (self.end_time - self.start_time).total_seconds()
        duration_hours = Decimal(duration_seconds) / Decimal(3600)

        self.total_price = (
                duration_hours * self.service.price_per_hour
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)

    # ================== Bekor qilish qoidalari ==================
    def can_cancel(self):
        now = timezone.now()
        if now >= self.start_time:
            return False  # allaqachon boshlangan yoki o‘tgan

        time_left = self.start_time - now
        hours_left = time_left.total_seconds() / 3600

        if hours_left >= 48:                    # 2 sutka va undan ko‘p
            return True
        elif 24 <= hours_left < 48:             # oxirgi 24 soat ichida
            return hours_left >= 26             # kamida 2 soat oldin
        elif 0 < hours_left < 24:               # o‘sha kuni
            return hours_left >= 1              # kamida 1 soat oldin
        return False

    # ================== Not attended ==================
    def can_mark_not_attended(self):
        """Admin qo‘lda 'not attended' belgilashi mumkinmi?"""
        if self.status != "in_progress":
            return False

        now = timezone.now()
        duration = self.end_time - self.start_time
        late_limit = self.start_time + duration * 0.4  # 40%

        return now > late_limit

    def mark_as_not_attended(self):
        """Admin tomonidan chaqiriladi"""
        if not self.can_mark_not_attended():
            raise ValidationError("Bu bookingni 'not attended' deb belgilash uchun hali vaqt yetmagan.")

        self.status = "not_attended"
        self.save(update_fields=["status"])

        # Userga strike berish
        user = self.user
        user.strike_count = models.F("strike_count") + 1
        user.save(update_fields=["strike_count"])
        user.refresh_from_db()

        now = timezone.now()

        if user.strike_count >= 5:
            user.blocked_until = now + timedelta(days=30)
        elif user.strike_count >= 3:
            user.blocked_until = now + timedelta(days=7)
        else:
            user.blocked_until = None

        user.save(update_fields=["blocked_until"])
        return True

    # ================== Lifecycle ==================
    def is_in_progress(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == "in_progress"

    def update_status_based_on_time(self):
        """Vaqtga qarab statusni avtomatik yangilash"""
        now = timezone.now()

        if self.status in ["cancelled", "completed", "not_attended"]:
            return

        if self.start_time <= now < self.end_time:
            self.status = "in_progress"
        elif now >= self.end_time:
            self.status = "completed"