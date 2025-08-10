from django.urls import path
from .views import (
    load_kebele_crop_csv_from_path,load_crop_csv_from_path
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('test/', load_crop_csv_from_path, name='register'),

]