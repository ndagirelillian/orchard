from django.db import models
from django.utils import timezone

class Staff(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    POSITION_CHOICES = [
        ('Manager', 'Manager'),
        ('Receptionist', 'Receptionist'),
        ('Housekeeping', 'Housekeeping'),
        ('Chef', 'Chef'),
        ('Security', 'Security'),
        ('Waiter', 'Waiter'),
        ('Other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    nin = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default='Other')
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"


class StaffAttendance(models.Model):
    ATTENDANCE_STATUS = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused'),
    ]

    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    time_in = models.TimeField(blank=True, null=True)
    date_out = models.DateField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default='Present')
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('staff', 'date')  # Prevent duplicate entries for same staff on the same day
        ordering = ['-date', 'time_in']

    def __str__(self):
        return f"{self.staff} - {self.date} - {self.status}"
