from django.contrib import admin
from django.contrib import admin
from .models import Doctor, DoctorAvailability

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialty', 'is_approved']
    list_filter = ['is_approved']
    actions = ['approve_doctors']
    
    def approve_doctors(self, request, queryset):
        queryset.update(is_approved=True)
    approve_doctors.short_description = 'Approve doctors'

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day', 'time_from', 'time_to']