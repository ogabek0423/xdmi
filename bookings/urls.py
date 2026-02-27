from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import cancel_booking, admin_calendar_day, dashboard_view, create_booking, home, BookingViewSet, admin_calendar

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path("", home, name="home"),
    path("book/", create_booking, name="book"),
    path('api', include(router.urls)),
    path('dashboard/', dashboard_view, name='dashboard'),
    path("cancel/<int:booking_id>/", cancel_booking, name="cancel_booking"),
    path('calendar/', admin_calendar, name='admin_calendar'),
    path('dashboard/calendar/day/<str:date_str>/', admin_calendar_day, name='admin_calendar_day'),
]