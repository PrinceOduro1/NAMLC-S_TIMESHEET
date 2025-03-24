from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

# Custom Employee Model (Extends Django's User Model)
class Employee(AbstractUser):
    username = models.CharField(max_length=100, unique=True, default=False)
    fullname = models.CharField(max_length=120,default=False)
    employee_id = models.CharField(max_length=10, unique=True)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    password = models.CharField(max_length=128, default=False)

    def __str__(self):
        return f"{self.employee_id} ({self.department})"

# Employee Timesheet Model for Sign-in and Sign-out
class EmployeeTimesheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Create relationship with Employee
    check_in_time = models.DateTimeField(null=True)  # Auto timestamp for sign-in
    check_out_time = models.DateTimeField(null=True, blank=True)  # Sign-out time
    hours_on_site = models.CharField(null=True, blank=True, max_length=30)
    hours_worked = models.IntegerField(null=True, blank=True)

    # Calculate total hours on site
    def calculate_hours(self):
        if self.check_out_time:
            minutes_worked = (self.check_out_time - self.check_in_time).total_seconds()/60
            hours = minutes_worked/60
            just_hours = int(hours)
            minutes_left = int(minutes_worked - (just_hours*60))

            return f"{just_hours} hours: {minutes_left} minutes"
        return None
    def calculate_int(self):
        if self.check_out_time:
            minutes_worked = (self.check_out_time - self.check_in_time).total_seconds()/60
            hours = minutes_worked/60
            just_hours = int(hours)

            return f"{just_hours} hours"
        return None

    # Auto-calculate hours before saving
    def save(self, *args, **kwargs):
        self.hours_on_site = self.calculate_hours()
        self.hours_worked = self.calculate_int()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employee_id}"
    
