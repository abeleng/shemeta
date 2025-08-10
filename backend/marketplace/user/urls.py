from django.urls import path
from .views import (
    register_view,
    CustomTokenObtainPairView,
    logout_view,
    add_land_detail_view,
    test_add_kebeles,
    load_recommendations,
    farmer_home_view,
    post_crop_requirement,
    exporter_home_view
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('add-land-detail/', add_land_detail_view, name='add_land_detail'),
    path('test/', test_add_kebeles, name='load_crop_csv'),
    path('load_recommendations/',load_recommendations),
    path('farmer_home/',farmer_home_view),
    path('post_crop_requirement/',post_crop_requirement),
    path('exporter_home/',exporter_home_view)
]