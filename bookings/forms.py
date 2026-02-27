from django import forms
from django.core.exceptions import ValidationError

from .models import Booking
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class BookingForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Boshlanish vaqti"
    )

    duration_hours = forms.DecimalField(
        min_value=Decimal('0.5'),
        max_value=Decimal('24'),
        decimal_places=1,
        initial=Decimal('1.0'),
        label="Davomiylik (soat)",
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.5', 'min': '0.5'})
    )

    class Meta:
        model = Booking
        fields = ["start_time", "people_count", "duration_hours"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields['start_time'].initial = timezone.now() + timedelta(hours=1)

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        duration_hours = cleaned_data.get("duration_hours") or Decimal('1.0')

        if start_time:
            end_time = start_time + timedelta(hours=float(duration_hours))
            cleaned_data["end_time"] = end_time

            # MUHIM QISM
            self.instance.user = self.user
            self.instance.service = self.service
            self.instance.start_time = start_time
            self.instance.end_time = end_time
            self.instance.people_count = cleaned_data.get("people_count", 1)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        instance.service = self.service
        instance.end_time = self.cleaned_data["end_time"]

        if commit:
            instance.save()

        return instance