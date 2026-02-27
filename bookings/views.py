from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import BookingSerializer
from django.db.models import Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, Service
import json
from .forms import BookingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import datetime, timedelta
from bookings.models import Booking


@staff_member_required
def admin_calendar(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Oy boshlanishi va tugashi
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

    # Har bir kun uchun bron sonini hisoblash
    calendar_data = []
    current = first_day
    while current <= last_day:
        count = Booking.objects.filter(start_time__date=current).count()

        calendar_data.append({
            'date': current,
            'count': count,
            'is_today': current == today,
        })
        current += timedelta(days=1)

    context = {
        'calendar_data': calendar_data,
        'year': year,
        'month': month,
        'month_name': first_day.strftime("%B %Y"),
        'prev_month': (first_day - timedelta(days=1)).strftime("%Y-%m"),
        'next_month': (last_day + timedelta(days=1)).strftime("%Y-%m"),
    }
    weeks = []
    week = []
    for day in calendar_data:
        week.append(day)
        if len(week) == 7 or day == calendar_data[-1]:
            weeks.append(week)
            week = []

    context['weeks'] = weeks
    return render(request, 'admin/calendar.html', context)

@staff_member_required
def admin_calendar_day(request, date_str):
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("<div class='alert alert-danger'>Noto‘g‘ri sana formati</div>", status=400)

    bookings = Booking.objects.filter(
        start_time__date=selected_date
    ).select_related('user', 'service__facility').order_by('start_time')

    if not bookings.exists():
        return HttpResponse("<p class='text-muted text-center py-4'>Bu kunda bron yo‘q</p>")

    html = """
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>User</th>
                    <th>Xizmat</th>
                    <th>Vaqt</th>
                    <th>Status</th>
                    <th>Narx</th>
                </tr>
            </thead>
            <tbody>
    """
    for booking in bookings:
        html += f"""
                <tr>
                    <td>{booking.user.email}</td>
                    <td>{booking.service.name} ({booking.service.facility.name})</td>
                    <td>{booking.start_time.strftime('%H:%M')} – {booking.end_time.strftime('%H:%M')}</td>
                    <td><span class="badge bg-{'warning' if booking.status == 'pending' else 'info' if booking.status == 'in_progress' else 'success'}">{booking.get_status_display()}</span></td>
                    <td>{booking.total_price} so'm</td>
                </tr>
    """
    html += """
            </tbody>
        </table>
    </div>
    """

    return HttpResponse(html)


def home(request):
    # Eng mashhur / yangi 6 ta xizmatni olish (masalan bron soni bo'yicha)
    popular_services = Service.objects.select_related('facility').annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')[:6]

    context = {
        'popular_services': popular_services,
        'title': 'Bosh sahifa',
    }
    return render(request, 'home.html', context)

@login_required
def create_booking(request):
    if request.user.blocked_until and request.user.blocked_until > timezone.now():
        messages.error(request, f"Siz bloklangansiz. Blok {request.user.blocked_until.strftime('%Y-%m-%d %H:%M')} gacha davom etadi.")
        return redirect("profile")  # yoki "home"
        # Alternativ: return HttpResponseForbidden("Siz bloklangansiz")

    # agar blok bo‘lmasa → davom etadi
    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save()
            messages.success(request, "Bron muvaffaqiyatli yaratildi!")
            return redirect("my_bookings")
    else:
        form = BookingForm(user=request.user)

    return render(request, "booking_form.html", {"form": form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "my_bookings.html", {"bookings": bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status not in ["pending", "in_progress"]:
        messages.error(request, "Bu bronni bekor qilib bo‘lmaydi.")
        return redirect("my_bookings")

    if not booking.can_cancel():
        messages.error(request, "Bekor qilish muddati o‘tib ketgan.")
        return redirect("my_bookings")

    booking.status = "cancelled"
    booking.save(update_fields=["status"])
    messages.success(request, "Bron bekor qilindi.")
    return redirect("my_bookings")


def dashboard_view(request):
    for booking in Booking.objects.filter(status__in=["pending", "in_progress"]):
        booking.update_status_based_on_time()

    today = timezone.now().date()

    # 🔹 Bugungi statistikalar
    today_bookings = Booking.objects.filter(
        start_time__date=today
    ).count()

    today_revenue = Booking.objects.filter(
        start_time__date=today,
        status__in=["completed"]
    ).aggregate(total=Sum("total_price"))["total"] or 0

    # 🔹 7 kunlik tushum
    last_7_days = []
    last_7_revenue = []
    last_7_bookings = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        revenue = Booking.objects.filter(
            start_time__date=day,
            status__in=["completed"]
        ).aggregate(total=Sum("total_price"))["total"] or 0

        bookings_count = Booking.objects.filter(
            start_time__date=day
        ).count()

        last_7_days.append(day.strftime("%d-%m"))
        last_7_revenue.append(float(revenue))
        last_7_bookings.append(bookings_count)

    # 🔹 Status statistikasi
    status_stats = Booking.objects.values("status").annotate(total=Count("id"))

    status_labels = [s["status"] for s in status_stats]
    status_counts = [s["total"] for s in status_stats]

    # 🔹 Eng ko‘p bron qilingan service
    top_services = Booking.objects.values("service__name").annotate(
        total=Count("id")
    ).order_by("-total")[:5]

    service_labels = [s["service__name"] for s in top_services]
    service_counts = [s["total"] for s in top_services]

    # 🔹 Service kesimida tushum
    revenue_by_service = Booking.objects.filter(
        status__in=["completed", "in_progress"]
    ).values("service__name").annotate(
        total=Sum("total_price")
    ).order_by("-total")[:5]

    revenue_service_labels = [r["service__name"] for r in revenue_by_service]
    revenue_service_values = [float(r["total"]) for r in revenue_by_service]

    # 🔹 Occupancy rate
    total_services = Service.objects.count()
    active_bookings = Booking.objects.filter(
        status__in=["pending", "in_progress"]
    ).count()

    occupancy_rate = 0
    if total_services > 0:
        occupancy_rate = round((active_bookings / total_services) * 100, 2)

    context = {
        "today_bookings": today_bookings,
        "today_revenue": today_revenue,
        "last_7_days": json.dumps(last_7_days),
        "last_7_revenue": json.dumps(last_7_revenue),
        "last_7_bookings": json.dumps(last_7_bookings),
        "status_labels": json.dumps(status_labels),
        "status_counts": json.dumps(status_counts),
        "service_labels": json.dumps(service_labels),
        "service_counts": json.dumps(service_counts),
        "revenue_service_labels": json.dumps(revenue_service_labels),
        "revenue_service_values": json.dumps(revenue_service_values),
        "occupancy_rate": occupancy_rate,
    }

    return render(request, "dashboard.html", context)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if not booking.can_cancel():
            return Response({"detail": "Bekor qilish uchun yetarli vaqt qolmadi."},
                            status=status.HTTP_400_BAD_REQUEST)
        booking.status = "cancelled"
        booking.save(update_fields=["status"])
        return Response({"detail": "Booking bekor qilindi."})

    @action(detail=False, methods=['post'])
    def update_statuses(self, request):
        bookings = self.get_queryset()
        for booking in bookings:
            booking.update_status_based_on_time()
        return Response({"detail": "Booking statuslari yangilandi."})