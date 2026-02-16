from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15,unique=True)
    specialty = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    experience = models.IntegerField(help_text="Years of experience")
    medical_council_no = models.CharField(max_length=50, unique=True)
    license_document = models.FileField(upload_to='doctor_licenses/')
    
    # Clinic information fields
    clinic_name = models.CharField(max_length=200, blank=True, null=True)
    clinic_address = models.TextField(blank=True, null=True)
    clinic_city = models.CharField(max_length=100, blank=True, null=True)
    clinic_state = models.CharField(max_length=100, blank=True, null=True)
    clinic_pincode = models.CharField(max_length=10, blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    is_approved = models.BooleanField(default=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialty}"

    class Meta:
        ordering = ['-created_at']


class DoctorAvailability(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    time_from = models.TimeField()
    time_to = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.day} ({self.time_from} - {self.time_to})"

    class Meta:
        ordering = ['day', 'time_from']
        unique_together = ['doctor', 'day']