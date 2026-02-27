from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Facility, Service
from bookings.forms import BookingForm
from django.shortcuts import render
from .models import Service
from django.db.models import Q


def service_list(request):
    services = Service.objects.select_related('facility').all()

    # Saralash parametrini olish
    sort = request.GET.get('sort', 'name')  # default: nom bo'yicha

    if sort == 'facility':
        services = services.order_by('facility__name')
    elif sort == 'price_asc':
        services = services.order_by('price_per_hour')
    elif sort == 'price_desc':
        services = services.order_by('-price_per_hour')
    elif sort == 'capacity':
        services = services.order_by('-capacity')
    else:
        services = services.order_by('name')  # default

    context = {
        'services': services,
        'title': 'Mavjud xizmatlar',
        'current_sort': sort,  # hozirgi saralashni saqlash uchun
    }
    return render(request, 'facilities/service_list.html', context)


@login_required
def service_detail(request, service_id):
    service = get_object_or_404(Service, pk=service_id)

    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user, service=service)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.service = service
            booking.save()

            messages.success(
                request,
                f"{service.name} uchun bron muvaffaqiyatli yaratildi!"
            )
            return redirect("profile")

        else:
            # Faqat bitta sikl yetarli
            for error in form.errors.values():
                for e in error:
                    messages.error(request, e)

    else:
        form = BookingForm(user=request.user, service=service)

    return render(request, 'facilities/service_detail.html', {
        'service': service,
        'form': form,
        'title': f"{service.name} - Bron qilish"
    })
#
# @login_required
# def facility_list(request):
#     """
#     Agar keyinchalik facility bo'yicha filtr yoki ro'yxat kerak bo'lsa
#     (hozircha oddiy variant)
#     """
#     facilities = Facility.objects.all().order_by('name')
#
#     context = {
#         'facilities': facilities,
#         'title': 'Barcha sport zallari va joylar',
#     }
#     return render(request, 'facilities/facility_list.html', context)
#
#
# # Agar kerak bo'lsa — facility detail sahifasi (masalan /facilities/1/)
# def facility_detail(request, facility_id):
#     facility = get_object_or_404(Facility, pk=facility_id)
#     services = facility.service_set.all().order_by('name')
#
#     context = {
#         'facility': facility,
#         'services': services,
#         'title': f"{facility.name} - Batafsil",
#     }
#     return render(request, 'facilities/facility_detail.html', context)