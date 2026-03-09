# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('verify/', views.verify, name='verify'),
    path('login/', views.login, name='login'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('edit-profile/', views.edit_patient_profile, name='edit_patient_profile'),
    path('logout/', views.logout, name='logout'),
]