from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from accounts.models import Patient
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from Appointments.models import Appointment
import datetime
from django.core.mail import send_mail
from django.conf import settings
import random
from django import forms


# ✅ PATIENT EDIT FORM
class PatientEditForm(forms.ModelForm):
    """Form for patients to edit their profile - simplified"""
    
    class Meta:
        model = Patient
        fields = ['phone', 'gender', 'age', 'address', 'bloodgroup']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
            }),
            'gender': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Male, Female, Other',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter age',
                'min': '1',
                'max': '120'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your address'
            }),
            'bloodgroup': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A+, B-, O+',
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not phone.isdigit() or len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
            existing = Patient.objects.filter(phone=phone).exclude(
                user=self.instance.user
            ).exists()
            if existing:
                raise forms.ValidationError("This phone number is already registered.")
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and (age < 1 or age > 120):
            raise forms.ValidationError("Age must be between 1 and 120.")
        return age


# ✅ USER EDIT FORM
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing = User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
            if existing:
                raise forms.ValidationError("This email is already registered.")
        return email


# ✅ PATIENT REGISTER FORM
class PatientRegisterForm(forms.Form):
    fname = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (10 digits)'})
    )
    age = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'})
    )
    gender = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gender'})
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3})
    )
    bloodgroup = forms.CharField(
        max_length=5,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Blood Group (e.g., A+, B-)'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        if Patient.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


# ✅ REGISTER VIEW
def register(request):
    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        
        if form.is_valid():
            fname = form.cleaned_data['fname']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            age = form.cleaned_data['age']
            gender = form.cleaned_data['gender']
            address = form.cleaned_data['address']
            bloodgroup = form.cleaned_data['bloodgroup']
            password = form.cleaned_data['password1']
            
            otp = str(random.randint(100000, 999999))
            
            request.session['pending_registration'] = {
                'fname': fname,
                'email': email,
                'phone': phone,
                'age': age,
                'gender': gender,
                'address': address,
                'bloodgroup': bloodgroup,
                'password': password,
                'otp': otp
            }
            
            try:
                send_mail(
                    subject="Your OTP for CareConnect",
                    message=f"Your OTP is: {otp}\n\nDo not share this OTP.",
                    from_email=settings.DEFAULT_FROM_EMAIL,  # ✅ FIXED
                    recipient_list=[email],
                    fail_silently=False
                )
                messages.success(request, "OTP sent to your email")
                return redirect("accounts:verify_otp")
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
                return redirect("accounts:register")
        
        else:
            return render(request, 'accounts/register.html', {'form': form})
    
    else:
        form = PatientRegisterForm()
        return render(request, 'accounts/register.html', {'form': form})


# ✅ VERIFY OTP VIEW
def verify_otp(request):
    pending = request.session.get('pending_registration')
    
    if not pending:
        messages.error(request, "Please register first")
        return redirect("accounts:register")
    
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        
        if not entered_otp:
            messages.error(request, "Please enter OTP")
            return render(request, 'accounts/verify.html')
        
        if entered_otp == pending['otp']:
            try:
                user = User.objects.create_user(
                    username=pending['email'],
                    email=pending['email'],
                    password=pending['password'],
                    first_name=pending['fname']
                )
                
                patient = Patient.objects.create(
                    user=user,
                    phone=pending['phone'],
                    age=pending['age'],
                    gender=pending['gender'],
                    address=pending['address'],
                    bloodgroup=pending['bloodgroup'],
                    otp=""
                )
                
                del request.session['pending_registration']
                auth_login(request, user)
                
                messages.success(request, "Account created successfully!")
                return redirect("accounts:patient_profile")
            
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect("accounts:register")
        
        else:
            messages.error(request, "Invalid OTP")
            return render(request, 'accounts/verify.html')
    
    return render(request, 'accounts/verify.html')


# ✅ RESEND OTP
def resend_otp(request):
    pending = request.session.get('pending_registration')
    
    if not pending:
        return redirect("accounts:register")
    
    new_otp = str(random.randint(100000, 999999))
    pending['otp'] = new_otp
    request.session['pending_registration'] = pending
    
    try:
        send_mail(
            subject="Your New OTP for CareConnect",
            message=f"Your OTP is: {new_otp}\n\nDo not share this OTP.",
            from_email=settings.DEFAULT_FROM_EMAIL,  # ✅ FIXED
            recipient_list=[pending['email']],
            fail_silently=False
        )
        messages.success(request, "New OTP sent to your email")
    except:
        messages.error(request, "Failed to send OTP")
    
    return redirect("accounts:verify_otp")


# ✅ LOGIN VIEW
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, "❌ Email and password are required.")
            return redirect('accounts:login')
        
        try:
            user_exists = User.objects.filter(username=email).exists()
            
            if not user_exists:
                messages.warning(request, "❌ Account not found. Please create an account first by clicking 'Sign up' below.")
                return render(request, 'accounts/login.html')
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                if user.last_name == "Reception":
                    return redirect('reception')
                elif user.last_name == "HR":
                    return redirect('Home:dashboard')
                else:
                    return redirect('Home:dashboard')
            else:
                messages.error(request, "❌ Invalid email or password.")
                return render(request, 'accounts/login.html')
        
        except Exception as e:
            messages.error(request, f"❌ Login error: {str(e)}")
            return render(request, 'accounts/login.html')
    
    else:
        return render(request, 'accounts/login.html')


@login_required
def verify(request):
    email = request.session.get('pending_email') or request.user.email
    
    try:
        user = User.objects.get(email=email)
        patient = Patient.objects.get(user=user)
    except (User.DoesNotExist, Patient.DoesNotExist):
        messages.error(request, "❌ Profile not found.")
        return redirect("accounts:register")
    
    if not patient.otp:
        messages.info(request, "✅ Your email is already verified.")
        return redirect("Home:dashboard")
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "verify":
            entered_otp = request.POST.get("otp", "").strip()
            
            if not entered_otp:
                messages.error(request, "❌ Please enter the OTP.")
                return render(request, "accounts/verify.html", {'patient': patient})
            
            if entered_otp == patient.otp:
                patient.otp = ""
                patient.save()
                
                if 'pending_email' in request.session:
                    del request.session['pending_email']
                
                messages.success(request, "✅ Email verified successfully!")
                return redirect("Home:dashboard")
            else:
                messages.error(request, "❌ Invalid OTP. Please try again.")
                return render(request, "accounts/verify.html", {'patient': patient})
        
        elif action == "resend":
            new_otp = str(random.randint(100000, 999999))
            patient.otp = new_otp
            patient.save()
            
            try:
                send_mail(
                    subject="Your New OTP for CareConnect",
                    message=(
                        f"Hi {patient.user.first_name},\n\n"
                        f"Your new OTP is: {new_otp}\n\n"
                        f"This OTP will expire in 10 minutes.\n"
                        f"Do not share this OTP with anyone.\n\n"
                        f"Regards,\nCareConnect Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,  # ✅ FIXED
                    recipient_list=[patient.user.email],
                    fail_silently=False
                )
                messages.success(request, "✅ New OTP sent to your email.")
            except Exception as e:
                messages.error(request, f"❌ Failed to send OTP: {str(e)}")
            
            return render(request, "accounts/verify.html", {'patient': patient})
    
    return render(request, "accounts/verify.html", {'patient': patient})


# ✅ PATIENT PROFILE VIEW
@login_required
def patient_profile(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "❌ Patient profile not found.")
        return redirect("accounts:login")
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    
    context = {
        "patient": patient,
        "total_appointments": appointments.count(),
        "latest_appointment": appointments.first(),
    }
    
    return render(request, "accounts/profile.html", context)


# ✅ EDIT PATIENT PROFILE VIEW
@login_required
def edit_patient_profile(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "❌ Patient profile not found.")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        patient_form = PatientEditForm(request.POST, instance=patient)
        user_form = UserEditForm(request.POST, instance=request.user)
        
        if patient_form.is_valid() and user_form.is_valid():
            patient_form.save()
            user_form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('accounts:patient_profile')
        else:
            context = {
                'patient_form': patient_form,
                'user_form': user_form,
                'patient': patient,
            }
            return render(request, 'accounts/edit_patient_profile.html', context)
    
    else:
        patient_form = PatientEditForm(instance=patient)
        user_form = UserEditForm(instance=request.user)
    
    context = {
        'patient_form': patient_form,
        'user_form': user_form,
        'patient': patient,
    }
    
    return render(request, 'accounts/edit_patient_profile.html', context)


# ✅ LOGOUT VIEW
def logout(request):
    auth_logout(request)
    messages.success(request, "✅ Logged out successfully.")
    return redirect('accounts:login')