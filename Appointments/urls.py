from django.urls import path
from . import views

app_name = "Appointments"

urlpatterns = [
    path("list/", views.appointment, name="appointment"),
    path("book/", views.patient_book, name="patient_book"),
    path("doctors/", views.book_appointment, name="book_appointment"),
    path("reception/", views.reception, name="reception"),
    path("deletepat/", views.deletepat, name="deletepat"),
    path("updatepat/", views.updatepat, name="updatepat"),
    path("createpat/", views.createpat, name="crtpat"),
]
