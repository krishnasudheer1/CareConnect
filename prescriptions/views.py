from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Patient
from django.contrib.auth.models import User
from .models import Prescription
from Appointments.models import Appointment
from Doctors.models import Doctor


@login_required
def addpres(request):
    doc = Doctor.objects.filter(user=request.user).first()
    p = Patient.objects.all()

    if request.method == 'POST':
        patname = request.POST['pat']
        pres = request.POST['pres']
        dis = request.POST['dis']

        us = User.objects.filter(first_name=patname).first()
        pat = Patient.objects.filter(user=us).first()

        Prescription.objects.create(
            prescription=pres,
            patient=pat,
            doctor=doc,
            disease=dis
        )
        return redirect("showpres")

    return render(request, 'prescriptions/addpres.html', {'p': p})


@login_required
def showpres(request):
    pre = Prescription.objects.all()
    return render(request, 'prescriptions/showpres.html', {'pre': pre})


@login_required
def showmedhis(request):
    patient = Patient.objects.filter(user=request.user).first()
    pre = Prescription.objects.filter(patient=patient)
    return render(request, 'prescriptions/showmedhis.html', {'pre': pre})


@login_required
def patient_history(request):
    patient = Patient.objects.filter(user=request.user).first()
    # doctors = Doctor.objects.all() 
    if not patient:
        return render(request, "prescriptions/patient_history.html", {
            "appointments": [],
            "count": 0
        })

    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related("doctor", "doctor__user").order_by("-date", "-time_from")

    return render(request, "prescriptions/patient_history.html", {
        "appointments": appointments,
        "count": appointments.count()
    })


@login_required
def delete_appointment(request, pk):
    patient = Patient.objects.filter(user=request.user).first()
    appointment = get_object_or_404(Appointment, pk=pk, patient=patient)

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")

    return redirect("patient_history")
