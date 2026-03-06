from django.urls import path
from .views import home, dashboard,logout_view

app_name = "Home"

urlpatterns=[
   
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
  

]
