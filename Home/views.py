from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from Appointments.models import Appointment
from accounts.models import Patient
from django.utils import timezone
import datetime

def home(request):
    return render(request, 'Home/home.html')
def logout_view(request):
    logout(request)
    return redirect('Home:home')
@login_required
def dashboard(request):
    user = request.user

    # SAFE queries (never crash)
    upcoming_count = Appointment.objects.filter(
        patient__user=user,
        date__gte=datetime.date.today()
    ).count()

    past_count = Appointment.objects.filter(
        patient__user=user,
        date__lt=datetime.date.today()
    ).count()

    total_count = Appointment.objects.filter(
        patient__user=user
    ).count()

    return render(request, "Home/dashboard.html", {
        "upcoming_count": upcoming_count,
        "past_count": past_count,
        "total_count": total_count
    })


