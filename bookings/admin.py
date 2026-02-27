from django.contrib import admin, messages
from django.utils.html import format_html
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from django.urls import path
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "service",
        "start_time",
        "end_time",
        "status",
        "total_price",
        "cancel_button",
    )
    actions = ["mark_not_attended"]

    # ====================== Admin Action ======================
    @admin.action(description="Mark selected bookings as Not Attended")
    def mark_not_attended(self, request, queryset):
        count = 0
        for booking in queryset:
            if booking.can_mark_not_attended():
                booking.mark_as_not_attended()
                count += 1

        if count > 0:
            messages.success(request, f"{count} ta booking 'Not Attended' deb belgilandi.")
        else:
            messages.warning(request, "Hech qanday booking belgilana olmadi. Hali user kelishi mumkin")

    # ====================== Cancel tugmasi ======================
    def cancel_button(self, obj):
        if obj.can_cancel() and obj.status == "pending":
            return format_html(
                '<a class="button" href="cancel/{}/" style="color:white; background:#07eb71;">. Cancel .</a>',
                obj.id
            )
        return format_html(
                '<a class="button"  style="color:white; background:#d9534f;">Time over</a>',
            )

    cancel_button.short_description = "Cancel"

    # ====================== Custom URL (Cancel) ======================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "cancel/<int:booking_id>/",
                self.admin_site.admin_view(self.cancel_booking),
                name="booking-cancel",
            ),
        ]
        return custom_urls + urls

    def cancel_booking(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            messages.error(request, f"Booking ID {booking_id} topilmadi.")
            return redirect(request.META.get("HTTP_REFERER", "admin:bookings_booking_changelist"))

        if not booking.can_cancel():
            messages.error(request, "Bekor qilish uchun vaqt qolmadi.")
        else:
            booking.status = "cancelled"
            booking.save(update_fields=["status"])
            messages.success(request, "✅ Booking muvaffaqiyatli bekor qilindi.")

        return redirect(request.META.get("HTTP_REFERER", "admin:bookings_booking_changelist"))
