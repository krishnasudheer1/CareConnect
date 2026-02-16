from django.urls import path
from . import views
urlpatterns=[
    path('addpres/',views.addpres,name='addpres'),
    path('showpres/',views.showpres,name='showpres'),
    path('showmedhis/',views.showmedhis,name='showmedhis'),
    path("history/", views.patient_history, name="patient_history"),

    path("delete/<int:pk>/", views.delete_appointment, name="delete_appointment")
]