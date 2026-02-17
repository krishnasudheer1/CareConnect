from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Appointment
from accounts.models import Patient
from Doctors.models import Doctor
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime 

# Create your views here.
@login_required
def appointment(request):
    # ✅ FILTERS ONLY APPROVED DOCTORS + PREFETCH AVAILABILITY
    doctors = Doctor.objects.filter(is_approved=True).select_related('user').prefetch_related('availabilities')

    # ✅ NEW: BUILD DOCTORS WITH AVAILABILITY DATA
    doctors_with_availability = []
    for doctor in doctors:
        availability = doctor.availabilities.all()
        
        # ✅ GET UNIQUE TIME SLOTS (remove duplicates)
        unique_times = []
        seen_times = set()
        for slot in availability:
            # Create a unique key from time_from and time_to
            time_key = f"{slot.time_from}-{slot.time_to}"
            if time_key not in seen_times:
                seen_times.add(time_key)
                unique_times.append(slot)
        
        doctors_with_availability.append({
            'doctor': doctor,
            'availability': availability,
            'unique_times': unique_times,  # ✅ Add deduped times
            'available_days': [a.day for a in availability],
        })

    pro = None
    ap = Appointment.objects.none()

    if request.user.last_name == "Patient":
        pro = Patient.objects.filter(user=request.user).first()
        ap = Appointment.objects.filter(patient=pro)

    elif request.user.last_name == "Doctor":
        pro = Doctor.objects.filter(user=request.user).first()
        ap = Appointment.objects.filter(doctor=pro)

    context = {
        "pro": pro,
        "ap": ap,
        "doctors": doctors_with_availability,
        "total_doctors": len(doctors_with_availability),
    }

    return render(request, "Appointments/book_appointments.html", context)

@login_required
def book_appointment(request):
    # ✅ FILTERS ONLY APPROVED DOCTORS + PREFETCH AVAILABILITY
    doctors = Doctor.objects.filter(is_approved=True).select_related('user').prefetch_related('availabilities')

    # ✅ NEW: BUILD DOCTORS WITH AVAILABILITY DATA
    doctors_with_availability = []
    for doctor in doctors:
        availability = doctor.availabilities.all()
        
        # ✅ GET UNIQUE TIME SLOTS (remove duplicates)
        unique_times = []
        seen_times = set()
        for slot in availability:
            # Create a unique key from time_from and time_to
            time_key = f"{slot.time_from}-{slot.time_to}"
            if time_key not in seen_times:
                seen_times.add(time_key)
                unique_times.append(slot)
        
        doctors_with_availability.append({
            'doctor': doctor,
            'availability': availability,
            'unique_times': unique_times,  # ✅ Add deduped times
            'available_days': [a.day for a in availability],
        })

    context = {
        "doctors": doctors_with_availability,
        "total_doctors": len(doctors_with_availability),
    }

    return render(request, "Appointments/book_appointments.html", context)


@login_required
def reception(request):
    ap = Appointment.objects.all()
    p = Patient.objects.all()
    tot = len(ap)
    pending = len(Appointment.objects.filter(status="Pending").all())
    com = len(Appointment.objects.filter(status="Completed").all())
    c = {'ap': ap, 'p': p, 'tot': tot, 'pend': pending, 'com': com}             
    return render(request, "Appointments/reception.html", c)


@login_required
def deletepat(request):
    if request.method == 'POST':
        pid = request.POST['pid']
        px = Patient.objects.filter(pid=pid).first()
        us = User.objects.filter(username=px.user.username).first()
        us.delete()
        return redirect("Appointments")
    ap = Appointment.objects.all()
    p = Patient.objects.all()
    c = {'ap': ap, 'p': p}             
    return render(request, "Appointments/reception.html", c)


@login_required
def createpat(request):
    if request.method == 'POST':        
        image = None
        try:
            _, file = request.FILES.popitem()
            file = file[0]
            image = file
        except:
            pass
        
        fname = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        gender = request.POST['gender']
        age = request.POST['age']
        add = request.POST['address']
        bg = request.POST['bloodgroup']
        casepaper = request.POST['casepaper']
        if User.objects.filter(username=email).exists():
            messages.info(request, "Email Id already Exists!")
            return redirect('crtpat')
        else:
            user = User.objects.create_user(first_name=fname, last_name='Patient', username=email, email=email)
            pro = Patient(user=user, phone=phone, gender=gender, age=age, address=add, bloodgroup=bg, casepaper=casepaper, image=image)
            pro.save()
            return redirect('reception')
    return render(request, 'Appointments/crtpat.html')

@login_required
def updatepat(request):
    if request.method == 'POST':
        pid = request.POST['pid']
        pro = Patient.objects.filter(pid=pid).first()
        return render(request, 'accounts/uprofile.html', {'pro': pro})


@login_required
@require_http_methods(["POST"])
def patient_book(request):
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        doctor_name = request.POST.get("doctor_name")
        doctor_specialty = request.POST.get("specialty")
        date = request.POST.get("date")
        time_from = request.POST.get("time_from")
        reason = request.POST.get("reason", "")

        # Validate required fields
        if not all([doctor_name, date, time_from]):
            error_msg = "❌ Missing required fields."
            if is_ajax:
                return JsonResponse({"success": False, "error": error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect("Appointments:appointment")

        # ✅ AUTO-CALCULATE time_to (30 minutes after time_from)
        from datetime import datetime, timedelta
        try:
            time_obj = datetime.strptime(time_from, "%H:%M")
            time_to_obj = time_obj + timedelta(minutes=30)
            time_to = time_to_obj.strftime("%H:%M")
            time = time_from
        except Exception as e:
            error_msg = "❌ Invalid time format."
            if is_ajax:
                return JsonResponse({"success": False, "error": error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect("Appointments:appointment")

        # Get patient
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            error_msg = "❌ Patient profile not found."
            if is_ajax:
                return JsonResponse({"success": False, "error": error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect("Appointments:appointment")
        
        # ✅ FIXED DOCTOR LOOKUP - Handles multi-word first names
        clean_name = doctor_name.replace("Dr. ", "").strip()
        
        doctor = None
        # Strategy 1: Try exact full name match (case-insensitive)
        for doc in Doctor.objects.filter(is_approved=True):
            if doc.user.get_full_name().lower() == clean_name.lower():
                doctor = doc
                break
        
        # Strategy 2: If not found, try matching last name + first part of first name
        if not doctor:
            name_parts = clean_name.split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
                for doc in Doctor.objects.filter(is_approved=True, user__last_name__iexact=last_name):
                    # Check if doctor's first name starts with the search first name
                    if doc.user.first_name.lower().startswith(name_parts[0].lower()):
                        doctor = doc
                        break
        
        # Strategy 3: Fallback - just first name
        if not doctor:
            name_parts = clean_name.split()
            if len(name_parts) >= 1:
                doctor = Doctor.objects.filter(
                    user__first_name__iexact=name_parts[0],
                    is_approved=True
                ).first()
        
        print(f"🔍 Doctor lookup: '{doctor_name}' → Found: {doctor}")

        # ✅ Check time slot using doctor object
        if doctor:
            if not Appointment.is_slot_available(
                doctor=doctor,
                date=date,
                time_from=time_from,
                time_to=time_to
            ):
                error_msg = "❌ This time slot is already booked. Please choose another time."
                if is_ajax:
                    return JsonResponse({"success": False, "error": error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect("Appointments:appointment")

        # Check if exact appointment already exists
        if Appointment.objects.filter(
            patient=patient,
            doctor=doctor,
            date=date,
            time_from=time_from
        ).exists():
            error_msg = "❌ This appointment already exists."
            if is_ajax:
                return JsonResponse({"success": False, "error": error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect("Appointments:appointment")

        # ✅ CREATE APPOINTMENT
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            doctor_name=doctor_name,
            doctor_specialty=doctor_specialty,
            date=date,
            time=time,
            time_from=time_from,
            time_to=time_to,
            reason=reason,
            status="Pending"
        )
        
        print(f"✅ APPOINTMENT CREATED: ID={appointment.id}, Patient={appointment.patient.user.username}, Doctor FK={appointment.doctor}, Doctor Name={appointment.doctor_name}, Date={appointment.date}")

        # Send email notification
        if doctor and doctor.user.email:
            print(f"📧 Sending email to: {doctor.user.email}")
            try:
                result = send_mail(
                    subject=f'🔔 New Appointment Booking - {patient.user.get_full_name()}',
                    message=f'''
Dear Dr. {doctor.user.get_full_name()},

You have a NEW APPOINTMENT BOOKING:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PATIENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {patient.user.get_full_name()}
Email: {patient.user.email}
Phone: {patient.phone if hasattr(patient, 'phone') else 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPOINTMENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {date}
Time: {time_from} - {time_to}
Reason: {reason if reason else 'Not specified'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please log in to your dashboard to manage this appointment.

Best regards,
BookMyDoctor Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[doctor.user.email],
                    fail_silently=False,
                )
                print(f"✅ Email sent successfully! Result: {result}")
            except Exception as e:
                print(f"❌ Email failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            if not doctor:
                print(f"⚠️ Email NOT sent - Doctor not found for '{doctor_name}'")
            elif not doctor.user.email:
                print(f"⚠️ Email NOT sent - Doctor {doctor.user.get_full_name()} has no email")

        # Return success response
        success_msg = "✅ Appointment booked successfully!"
        if is_ajax:
            return JsonResponse({
                "success": True,
                "message": success_msg,
                "appointment_id": appointment.id
            })
        
        messages.success(request, success_msg)
        return redirect("Appointments:appointment")

    except Exception as e:
        print(f"❌ ERROR in patient_book: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_msg = f"❌ Failed to book appointment: {str(e)}"
        if is_ajax:
            return JsonResponse({"success": False, "error": error_msg}, status=500)
        
        messages.error(request, error_msg)
        return redirect("Appointments:appointment")