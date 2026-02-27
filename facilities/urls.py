from django.urls import path
from .views import service_list, service_detail

app_name = 'facilities'

urlpatterns = [
    path('', service_list, name='service_list'),
    path('<int:service_id>/', service_detail, name='service_detail'),
]