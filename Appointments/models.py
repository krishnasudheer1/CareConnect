from django.db import models
from accounts.models import Patient
from Doctors.models import Doctor
from datetime import datetime  # ✅ ADD THIS


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    
    # PRIMARY doctor reference - this should be the main field
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True, related_name='appointments')
    
    # DEPRECATED - Keep for backward compatibility but should be auto-populated
    doctor_name = models.CharField(max_length=255, blank=True)
    doctor_specialty = models.CharField(max_length=100, blank=True)

    date = models.DateField()
    time = models.TimeField()
    
    time_from = models.TimeField(null=True, blank=True)
    time_to = models.TimeField(null=True, blank=True)
    
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor', 'date', 'time')  # Changed from doctor_name to doctor
        ordering = ['-created_at']

    def __str__(self):
        doctor_display = self.doctor.user.get_full_name() if self.doctor else self.doctor_name
        return f"{self.patient} - {doctor_display} ({self.date} {self.time})"

    def save(self, *args, **kwargs):
        # Auto-populate doctor_name and doctor_specialty from doctor ForeignKey
        if self.doctor:
            self.doctor_name = self.doctor.user.get_full_name()
            self.doctor_specialty = self.doctor.specialty
        super().save(*args, **kwargs)

    @classmethod
    def is_slot_available(cls, doctor, date, time_from, time_to):
        """
        Prevent overlapping bookings for the same doctor & date
        ✅ FIXED: Converts string times to time objects before comparison
        """
        # ✅ CONVERT STRING TIMES TO TIME OBJECTS
        if isinstance(time_from, str):
            time_from = datetime.strptime(time_from, "%H:%M").time()
        if isinstance(time_to, str):
            time_to = datetime.strptime(time_to, "%H:%M").time()
        
        existing = cls.objects.filter(
            doctor=doctor,
            date=date
        )

        for appt in existing:
            if appt.time and not appt.time_from:
                if appt.time == time_from:
                    return False

            if appt.time_from and appt.time_to:
                if time_from < appt.time_to and time_to > appt.time_from:
                    return False

        return True

        