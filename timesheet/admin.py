from django.contrib import admin
from .models import Employee,EmployeeTimesheet
# Register your models here.
admin.site.register(Employee)
admin.site.register(EmployeeTimesheet)