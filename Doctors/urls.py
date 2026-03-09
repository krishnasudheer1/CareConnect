from django.urls import path
from . import views
app_name = 'Doctors'

urlpatterns = [
    # Doctor registration flow
    path('register/', views.doctor_register_start, name='doctor_register_start'),
    path('register/step1/', views.doctor_register_step1, name='doctor_register_step1'),
    path('register/step2/', views.doctor_register_step2, name='doctor_register_step2'),
    path('register/step3/', views.doctor_register_step3, name='doctor_register_step3'),
    path('register/step4/', views.doctor_register_step4, name='doctor_register_step4'),
    path('register/complete/', views.doctor_registration_complete, name='doctor_registration_complete'),
]