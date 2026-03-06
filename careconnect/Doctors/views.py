from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.db import transaction
from datetime import datetime

from .models import Doctor, DoctorAvailability


def doctor_register_start(request):
    """Landing page for doctor registration"""
    return render(request, 'Doctors/register_start.html')


def doctor_register_step1(request):
    """Step 1: Basic personal information"""
    # Load existing data from session (for back navigation or error retention)
    form_data = request.session.get('doctor_step1', {})
    
    if request.method == 'POST':
        # Capture ALL form data immediately
        form_data = {
            'first_name': request.POST.get('first_name', '').strip(),
            'last_name': request.POST.get('last_name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'username': request.POST.get('username', '').strip(),
        }
        
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validation - ALL DATA RETAINED, just show error message
        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please re-enter your passwords.')
            # ALL other fields stay filled
            return render(request, 'Doctors/register_step1.html', {'form_data': form_data})

        if User.objects.filter(username=form_data['username']).exists():
            messages.error(request, f'Username "{form_data["username"]}" already exists. Please choose a different username.')
            # ALL fields stay filled, user just changes username
            return render(request, 'Doctors/register_step1.html', {'form_data': form_data})

        if User.objects.filter(email=form_data['email']).exists():
            messages.error(request, f'Email "{form_data["email"]}" is already registered. Please use a different email.')
            # ALL fields stay filled, user just changes email
            return render(request, 'Doctors/register_step1.html', {'form_data': form_data})

        if Doctor.objects.filter(phone=form_data['phone']).exists():
            messages.error(request, f'Phone number "{form_data["phone"]}" is already registered. Please use a different phone number.')
            # ALL fields stay filled, user just changes phone
            return render(request, 'Doctors/register_step1.html', {'form_data': form_data})

        # All validations passed - Save to session INCLUDING password
        form_data['password'] = password  # Store password for final user creation
        request.session['doctor_step1'] = form_data
        request.session.modified = True

        messages.success(request, 'Step 1 completed successfully!')
        return redirect('Doctors:doctor_register_step2')

    # GET request or error - show form with existing data
    return render(request, 'Doctors/register_step1.html', {'form_data': form_data})


def doctor_register_step2(request):
    """Step 2: Professional information"""
    # Check if step 1 is completed
    if 'doctor_step1' not in request.session:
        messages.warning(request, 'Please complete Step 1 first')
        return redirect('Doctors:doctor_register_step1')

    # Load existing data from session
    form_data = request.session.get('doctor_step2', {})

    if request.method == 'POST':
        # Handle "Back" button - save current data and go back
        if 'back' in request.POST:
            # Save whatever user has typed before going back
            current_data = {
                'specialty': request.POST.get('specialty', '').strip(),
                'qualification': request.POST.get('qualification', '').strip(),
                'experience': request.POST.get('experience', '').strip(),
                'medical_council_no': request.POST.get('medical_council_no', '').strip(),
            }
            request.session['doctor_step2'] = current_data
            request.session.modified = True
            return redirect('Doctors:doctor_register_step1')

        # Capture ALL form data immediately
        form_data = {
            'specialty': request.POST.get('specialty', '').strip(),
            'qualification': request.POST.get('qualification', '').strip(),
            'experience': request.POST.get('experience', '').strip(),
            'medical_council_no': request.POST.get('medical_council_no', '').strip(),
        }

        # Validation - ALL DATA RETAINED
        if Doctor.objects.filter(medical_council_no=form_data['medical_council_no']).exists():
            messages.error(request, f'Medical Council Number "{form_data["medical_council_no"]}" already exists. Please enter a different registration number.')
            # ALL fields stay filled
            return render(request, 'Doctors/register_step2.html', {'form_data': form_data})

        # Validate experience is a valid positive number
        try:
            exp_value = int(form_data['experience'])
            if exp_value < 0:
                messages.error(request, 'Experience cannot be negative. Please enter a valid number of years.')
                # ALL fields stay filled
                return render(request, 'Doctors/register_step2.html', {'form_data': form_data})
        except ValueError:
            messages.error(request, f'"{form_data["experience"]}" is not a valid number. Please enter years of experience as a number (e.g., 5).')
            # ALL fields stay filled
            return render(request, 'Doctors/register_step2.html', {'form_data': form_data})

        # All validations passed - Save to session
        request.session['doctor_step2'] = form_data
        request.session.modified = True

        messages.success(request, 'Step 2 completed successfully!')
        return redirect('Doctors:doctor_register_step3')

    # GET request or error - show form with existing data
    return render(request, 'Doctors/register_step2.html', {'form_data': form_data})


def doctor_register_step3(request):
    """Step 3: Clinic information"""
    # Check if previous steps are completed
    if 'doctor_step1' not in request.session or 'doctor_step2' not in request.session:
        messages.warning(request, 'Please complete previous steps first')
        return redirect('Doctors:doctor_register_step1')

    # Load existing data from session
    form_data = request.session.get('doctor_step3', {})

    if request.method == 'POST':
        # Handle "Back" button - save current data and go back
        if 'back' in request.POST:
            # Save whatever user has typed before going back
            current_data = {
                'clinic_name': request.POST.get('clinic_name', '').strip(),
                'clinic_address': request.POST.get('clinic_address', '').strip(),
                'clinic_city': request.POST.get('clinic_city', '').strip(),
                'clinic_state': request.POST.get('clinic_state', '').strip(),
                'clinic_pincode': request.POST.get('clinic_pincode', '').strip(),
                'consultation_fee': request.POST.get('consultation_fee', '').strip(),
            }
            request.session['doctor_step3'] = current_data
            request.session.modified = True
            return redirect('doctors:doctor_register_step2')

        # Capture ALL form data immediately
        form_data = {
            'clinic_name': request.POST.get('clinic_name', '').strip(),
            'clinic_address': request.POST.get('clinic_address', '').strip(),
            'clinic_city': request.POST.get('clinic_city', '').strip(),
            'clinic_state': request.POST.get('clinic_state', '').strip(),
            'clinic_pincode': request.POST.get('clinic_pincode', '').strip(),
            'consultation_fee': request.POST.get('consultation_fee', '').strip(),
        }

        # Validate consultation fee
        try:
            fee_value = float(form_data['consultation_fee'])
            if fee_value < 0:
                messages.error(request, 'Consultation fee cannot be negative. Please enter a valid amount.')
                # ALL fields stay filled
                return render(request, 'Doctors/register_step3.html', {'form_data': form_data})
        except ValueError:
            messages.error(request, f'"{form_data["consultation_fee"]}" is not a valid amount. Please enter consultation fee as a number (e.g., 500).')
            # ALL fields stay filled
            return render(request, 'Doctors/register_step3.html', {'form_data': form_data})

        # Validate pincode is 6 digits
        if not form_data['clinic_pincode'].isdigit() or len(form_data['clinic_pincode']) != 6:
            messages.error(request, f'"{form_data["clinic_pincode"]}" is not a valid pincode. Please enter a 6-digit pincode.')
            # ALL fields stay filled
            return render(request, 'Doctors/register_step3.html', {'form_data': form_data})

        # All validations passed - Save to session
        request.session['doctor_step3'] = form_data
        request.session.modified = True

        messages.success(request, 'Step 3 completed successfully!')
        return redirect('Doctors:doctor_register_step4')

    # GET request or error - show form with existing data
    return render(request, 'Doctors/register_step3.html', {'form_data': form_data})


def doctor_register_step4(request):
    """Step 4: Availability and license upload (final step)"""
    # Check if all previous steps are completed
    if not all(k in request.session for k in ['doctor_step1', 'doctor_step2', 'doctor_step3']):
        messages.warning(request, 'Please complete all previous steps')
        return redirect('Doctors:doctor_register_step1')

    # Load existing data from session
    form_data = request.session.get('doctor_step4', {})

    if request.method == 'POST':
        # Handle "Back" button - save current data and go back
        if 'back' in request.POST:
            # Save whatever user has selected before going back
            current_data = {
                'available_days': request.POST.getlist('days'),
                'time_from': request.POST.get('time_from', '').strip(),
                'time_to': request.POST.get('time_to', '').strip(),
            }
            request.session['doctor_step4'] = current_data
            request.session.modified = True
            return redirect('Doctors:doctor_register_step3')

        try:
            with transaction.atomic():
                # Get session data from previous steps
                step1 = request.session['doctor_step1']
                step2 = request.session['doctor_step2']
                step3 = request.session['doctor_step3']

                # Capture ALL form data immediately
                available_days = request.POST.getlist('days')
                time_from_str = request.POST.get('time_from', '').strip()
                time_to_str = request.POST.get('time_to', '').strip()
                license_document = request.FILES.get('license')

                # Store current form data
                form_data = {
                    'available_days': available_days,
                    'time_from': time_from_str,
                    'time_to': time_to_str,
                }

                # Validation - ALL DATA RETAINED
                if not available_days:
                    messages.error(request, 'Please select at least one available day.')
                    return render(request, 'doctors/register_step4.html', {'form_data': form_data})

                if not time_from_str or not time_to_str:
                    messages.error(request, 'Please provide both start and end consultation times.')
                    return render(request, 'doctors/register_step4.html', {'form_data': form_data})

                if not license_document:
                    messages.error(request, 'Please upload your medical license document.')
                    return render(request, 'doctors/register_step4.html', {'form_data': form_data})

                # Validate file size (max 10MB)
                if license_document.size > 10 * 1024 * 1024:
                    messages.error(request, 'License file is too large. Maximum size is 10MB.')
                    return render(request, 'doctors/register_step4.html', {'form_data': form_data})

                # Validate file extension
                allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
                file_ext = license_document.name.lower()[license_document.name.rfind('.'):]
                if file_ext not in allowed_extensions:
                    messages.error(request, f'Invalid file type "{file_ext}". Please upload PDF, JPG, or PNG file.')
                    return render(request, 'doctors/register_step4.html', {'form_data': form_data})

                # Parse and validate time
                try:
                    time_from = datetime.strptime(time_from_str, "%H:%M").time()
                    time_to = datetime.strptime(time_to_str, "%H:%M").time()
                except ValueError:
                    messages.error(request, 'Invalid time format. Please select valid times.')
                    return render(request, 'doctors/register_step4.html', {'form_data': form_data})

                # Validate time range
                if time_from >= time_to:
                    messages.error(request, f'End time ({time_to_str}) must be after start time ({time_from_str}).')
                    return render(request, 'doctors/register_step4.html', {'form_data': form_data})

                # All validations passed - Create user and doctor profile
                user = User.objects.create_user(
                    username=step1['username'],
                    email=step1['email'],
                    password=step1['password'],
                    first_name=step1['first_name'],
                    last_name=step1['last_name'],
                )

                # Create doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    phone=step1['phone'],
                    specialty=step2['specialty'],
                    qualification=step2['qualification'],
                    experience=int(step2['experience']),
                    medical_council_no=step2['medical_council_no'],
                    consultation_fee=step3['consultation_fee'],
                    clinic_name=step3['clinic_name'],
                    clinic_address=step3['clinic_address'],
                    clinic_city=step3['clinic_city'],
                    clinic_state=step3['clinic_state'],
                    clinic_pincode=step3['clinic_pincode'],
                    license_document=license_document,
                    is_approved=False,
                )

                # Create availability records
                for day in available_days:
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        day=day,
                        time_from=time_from,
                        time_to=time_to
                    )

                # Clear all session data
                for k in ['doctor_step1', 'doctor_step2', 'doctor_step3', 'doctor_step4']:
                    request.session.pop(k, None)
                request.session.modified = True

                # Log in the user automatically
                login(request, user)
                
                messages.success(request, 'Registration completed successfully!')
                return redirect('Doctors:doctor_registration_complete')

        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
            return render(request, 'Doctors/register_step4.html', {'form_data': form_data})

    # GET request or error - show form with existing data
    return render(request, 'Doctors/register_step4.html', {'form_data': form_data})


def doctor_registration_complete(request):
    """Registration completion page"""
    return render(request, 'Doctors/registration_complete.html')