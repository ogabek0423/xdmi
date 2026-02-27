from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.utils import timezone
from bookings.models import Booking
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomPasswordChangeForm


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # commit=False — hali saqlamaymiz
            raw_password = form.cleaned_data.get('password1')  # yoki 'password2'
            user.set_password(raw_password)  # ← eng muhim qator! Xeshlaydi
            user.save()  # endi saqlaymiz (xeshlangan holda)

            login(request, user)  # avto login
            return redirect("home")  # yoki "profile" / "dashboard"
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})

@login_required
def edit_profile(request):
    if request.method == "POST":
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()
            password_form.save()  # parolni yangilaydi
            messages.success(request, "Ma'lumotlar va parol muvaffaqiyatli yangilandi!")
            return redirect("profile")
        else:
            messages.error(request, "Forma xatolari bor. Tekshirib ko'ring.")
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'title': "Profilni tahrirlash",
    }
    return render(request, "edit_profile.html", context)

@login_required
def profile(request):
    # Foydalanuvchining barcha bronlari (eng yangisidan boshlab)
    bookings = Booking.objects.filter(
        user=request.user
    ).select_related('service__facility').order_by('-start_time')

    context = {
        'user': request.user,
        'blocked_until_local': timezone.localtime(request.user.blocked_until) if request.user.blocked_until else None,
        'bookings': bookings,                    # ← eng muhim qator!
        'now': timezone.now(),                   # bekor qilish muddati uchun kerak
    }
    return render(request, "profile.html", context)

def logout_view(request):
    logout(request)
    return redirect("home")