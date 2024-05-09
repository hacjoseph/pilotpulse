from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.authorize_fitbit, name='fitbit_auth'),
    path('callback/', views.fitbit_callback, name='fitbit_callback'),
    path('refresh/', views.refresh_access_token, name='fitbit_refresh'),
    path('heartrate/', views.retrieve_heart_rate_data, name='fitbit_heartrate'),
]
