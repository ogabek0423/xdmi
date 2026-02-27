from django.db import models

class Facility(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()

    # Yangi maydon
    map_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Xarita havolasi (Google Maps)",
        help_text="Google Mapsdan joyni ulashgan linkni bu yerga qo‘ying"
    )

    # yoki koordinatalar bilan ishlash uchun (keyinchalik kengaytirish mumkin)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    is_exclusive = models.BooleanField(default=False)

    # Yangi maydon
    image = models.ImageField(
        upload_to='services/',
        null=True,
        blank=True,
        verbose_name="Xizmat rasmi"
    )

    def __str__(self):
        return f"{self.name} - {self.facility.name}"