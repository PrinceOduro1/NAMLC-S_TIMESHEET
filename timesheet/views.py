from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.http import HttpResponse
import pandas as pd
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib import messages
import openpyxl
from io import BytesIO
from datetime import datetime
from .models import Employee, EmployeeTimesheet
from django.http import JsonResponse
from django.utils import timezone
from django.db import models


def index(request):

    return render(request,'index.html')

# Check if user is admin
def is_admin(user):
    return user.is_superuser

# Manual User Registration View
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        employee_id = request.POST.get('employee_id')
        password = request.POST.get('password')
        department = request.POST.get('department')
        role = request.POST.get('role')
        fullname = request.POST.get('fullname')

        if Employee.objects.filter(employee_id=employee_id).exists():
            messages.error(request, "Employee ID already exists!")
            return redirect('register')

        
        user = Employee.objects.create_user(username=username,
            fullname = fullname,
            employee_id=employee_id,
            department=department,
            role=role,
            password=password)
        
        user.save()
    
    return render(request, 'register.html')
from django.contrib.auth.hashers import check_password  # Import check_password


from django.utils import timezone  # Import Django's timezone
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import Employee, EmployeeTimesheet

def sign_in(request):
    if request.method == "POST":
        employee_id = request.POST['employee_id']
        password = request.POST['password']
        check_in_time = timezone.now()  # Use timezone-aware datetime

        try:
            # Retrieve the employee by their employee ID
            employee = Employee.objects.get(employee_id=employee_id)

            # Check if the entered password matches the stored password
            if check_password(password, employee.password):
                today = check_in_time.date()

                # Get the most recent sign-in entry for this employee
                last_entry = EmployeeTimesheet.objects.filter(
                    employee=employee
                ).order_by('-check_in_time').first()

                if last_entry:
                    time_difference = check_in_time - last_entry.check_in_time
                    
                    # Check if they signed in but never signed out
                    if last_entry.check_out_time is None:
                        if time_difference.total_seconds() < 43200:  # Less than 12 hours
                            messages.error(request, "You must sign out first before signing in again.")
                            return redirect('sign_in')
                    else:
                        # If they signed out, allow new sign-in
                        pass

                # **Delete yesterday's entry if they didn't sign out**
                yesterday = today - timedelta(days=1)
                EmployeeTimesheet.objects.filter(
                    employee=employee,
                    check_in_time__date=yesterday,
                    check_out_time__isnull=True  # Only remove entries with no sign-out
                ).delete()

                # **Save new sign-in**
                EmployeeTimesheet.objects.create(employee=employee, check_in_time=check_in_time)
                messages.success(request, "Sign-in successful!")
                return redirect('sign_in')  # Redirect to the main dashboard

            else:
                messages.error(request, "Incorrect password. Please try again.")
                return redirect('sign_in')

        except Employee.DoesNotExist:
            messages.error(request, "Employee ID not found. Please try again.")
            return redirect('sign_in')

    return render(request, 'sign_in.html')

def sign_out(request):
    if request.method == "POST":
        employee_id = request.POST['employee_id']
        password = request.POST['password']
        check_out_time = now()  # Use the current time for check-out time
        print(check_out_time)

        try:
            # Retrieve the employee by their employee ID
            employee = Employee.objects.get(employee_id=employee_id)
            
            # Check if the entered password matches the stored password
            if check_password(password, employee.password):
                # Retrieve the timesheet entry for the employee (where check_in_time is not null)
                timesheet = EmployeeTimesheet.objects.filter(employee=employee, check_in_time__isnull=False).last()

                if timesheet:
                    # Update the existing timesheet with the check_out_time
                    timesheet.check_out_time = check_out_time
                    timesheet.save()
                    return redirect('index')  # Redirect to a dashboard or another page on successful sign-out
                else:
                    # If no matching check-in time is found
                    error_message = "No check-in record found. Please check if you have signed in first."
                    return render(request, 'sign_out.html', {'error_message': error_message})
            else:
                # If password is incorrect, show an error message
                error_message = "Incorrect password. Please try again."
                return render(request, 'sign_out.html', {'error_message': error_message})
        except Employee.DoesNotExist:
            # If the employee ID doesn't exist in the database
            error_message = "Employee ID not found. Please try again."
            return render(request, 'sign_out.html', {'error_message': error_message})

    return render(request, 'sign_out.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # If user is admin, redirect to admin dashboard
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                return redirect('index')  # Regular user redirection
        
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    
    return render(request, 'login.html')

# Admin Dashboard (Summary)
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_employees = Employee.objects.count()
    employees_on_site = EmployeeTimesheet.objects.filter(check_out_time__isnull=True).count()
    employees_per_department = Employee.objects.values('department').annotate(count=Count('department'))
    
    context = {
        'total_employees': total_employees,
        'employees_on_site': employees_on_site,
        'employees_per_department': employees_per_department
    }
    return render(request, 'admin_dashboard.html', context)



def get_employee_attendance_data(request):
    # Get the current date (today's date)
    today = timezone.now().date()  # We use .date() to ignore the time part
    
    # Get the number of check-ins for each department today
    check_ins_by_dept = EmployeeTimesheet.objects.filter(
        check_in_time__date=today  # Filter only today's date
    ).values('employee__department').annotate(check_in_count=models.Count('employee'))

    # Get the total number of check-ins for today
    total_check_ins = EmployeeTimesheet.objects.filter(
        check_in_time__date=today
    ).count()

    # Get the total number of check-ins for today
    total_check_out = EmployeeTimesheet.objects.filter(
        check_out_time__date=today
    ).count()
    active_employees = total_check_ins - total_check_out

    # Create a dictionary of department and check-in counts
    department_data = {entry['employee__department']: entry['check_in_count'] for entry in check_ins_by_dept}

    # Return the data as JSON, including the total check-ins for today
    return JsonResponse( {
        'attendance_data': department_data,
        'total_check_ins': total_check_ins,
        'total_check_out': total_check_out,
        'active_employees': active_employees
    })

from datetime import timedelta
@user_passes_test(is_admin)
def view_sheet(request):
    # Get today's date
    today = timezone.now().date()

    # Get the selected time range from the query parameter (default to "today")
    time_range = request.GET.get('time_range', 'today')

    # Get the date range based on the selected filter
    if time_range == 'today':
        start_date = today
        end_date = today
    elif time_range == 'one_week':
        start_date = today - timedelta(weeks=1)
        end_date = today
    elif time_range == 'one_month':
        start_date = today - timedelta(weeks=4)
        end_date = today
    elif time_range == 'one_year':
        start_date = today - timedelta(days=365)
        end_date = today
    elif time_range == 'all':
        # No filtering, fetch all timesheets
        timesheets = EmployeeTimesheet.objects.all().select_related('employee')
        return render(request, 'view_sheet.html', {'timesheets': timesheets, 'time_range': time_range})
    else:
        # Default to today if no valid filter is provided
        start_date = today
        end_date = today

    # Fetch employee timesheets for the selected date range
    timesheets = EmployeeTimesheet.objects.filter(check_in_time__date__range=[start_date, end_date]).select_related('employee')

    return render(request, 'view_sheet.html', {'timesheets': timesheets, 'time_range': time_range})

import requests
from openpyxl.drawing.image import Image
from django.utils.timezone import datetime as timezone_datetime
from PIL import Image as PILImage

@user_passes_test(is_admin)
def download_timesheets(request):
    # Get the filter and search parameters
    time_range = request.GET.get('time_range', 'all')  # Default to 'all' if no filter is applied
    search_query = request.GET.get('search', '')  # Default to empty string if no search is applied

    # Filter the timesheets based on the time range
    if time_range == 'today':
        timesheets = EmployeeTimesheet.objects.filter(check_in_time__date=datetime.today().date())
    elif time_range == 'one_week':
        timesheets = EmployeeTimesheet.objects.filter(check_in_time__gte=datetime.today() - timedelta(weeks=1))
    elif time_range == 'one_month':
        timesheets = EmployeeTimesheet.objects.filter(check_in_time__gte=datetime.today() - timedelta(days=30))
    elif time_range == 'one_year':
        timesheets = EmployeeTimesheet.objects.filter(check_in_time__gte=datetime.today() - timedelta(days=365))
    else:
        timesheets = EmployeeTimesheet.objects.all()

    # Apply the search query filter (search by employee ID)
    if search_query:
        timesheets = timesheets.filter(employee__employee_id__icontains=search_query)

    # Create a new workbook and add a sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = 'Timesheets'

    # Insert the logo (fetching the image from the URL)
    logo_url = 'https://nguvumining.com/wp-content/uploads/2023/02/nguvu_black-retina.png'  # Your logo URL here
    try:
        # Download the image from the URL
        response = requests.get(logo_url)
        img = PILImage.open(BytesIO(response.content))  # Open image using Pillow
        
        # Resize the image to fit in the cell (width: 100px, height: 50px)
        img = img.resize((100, 50), PILImage.Resampling.LANCZOS)  # Resize the image (adjust the size as needed)
        
        # Save the resized image to a BytesIO object
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Create openpyxl Image from the resized image
        openpyxl_img = Image(img_byte_arr)
        sheet.merge_cells('A1:B2')  # Merge cells for logo and title
        sheet.add_image(openpyxl_img, 'A1')  # Add the logo at position A1
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch logo from URL: {e}")
    
    # Add title and date of printing
    sheet.merge_cells('C1:H1')  # Merge cells for the title area
    sheet['C1'] = 'DAILY ATTENDANCE SHEET'  # Title in the header row
    sheet['C1'].font = openpyxl.styles.Font(size=16, bold=True)  # Make title bold and larger font
    sheet['C1'].alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center')

    # Add shift title
    sheet.merge_cells('C2:H2')  # Merge cells for the title area
    sheet['C2'] = 'SHIFT: DAY/NIGHT'  # Title in the header row
    sheet['C2'].font = openpyxl.styles.Font(size=11)  # Make title bold and larger font
    sheet['C2'].alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center')

    # Add the date of printing in the top-right corner
    sheet['L1'] = 'Date of Download: ' + timezone.now().strftime('%Y-%m-%d')
    sheet['L1'].alignment = openpyxl.styles.Alignment(horizontal='right')  # Align date to the right

        # Now add headers starting from A3
    sheet['A3'] = 'NO.'
    sheet['B3'] = 'Employee ID'
    sheet['C3'] = 'TIME IN'
    sheet['D3'] = 'TIME OUT'
    sheet['E3'] = 'HOURS WORKED'

    # Apply font style individually to each header cell
    font_style = openpyxl.styles.Font(size=11, bold=True)
    sheet['A3'].font = font_style
    sheet['B3'].font = font_style
    sheet['C3'].font = font_style
    sheet['D3'].font = font_style
    sheet['E3'].font = font_style


    # Add the filtered timesheet data starting from row 4
    for index, timesheet in enumerate(timesheets, start=1):
        # Ensure the check-in and check-out times are naive datetime objects and format them
        check_in_time = timesheet.check_in_time.replace(tzinfo=None) if timesheet.check_in_time else None
        check_out_time = timesheet.check_out_time.replace(tzinfo=None) if timesheet.check_out_time else None
        
        # Format datetime to a string (e.g., 'YYYY-MM-DD HH:MM:SS')
        check_in_time_str = check_in_time.strftime('%Y-%m-%d %H:%M:%S') if check_in_time else ''
        check_out_time_str = check_out_time.strftime('%Y-%m-%d %H:%M:%S') if check_out_time else ''

        row = [
            index,
            timesheet.employee.employee_id,
            check_in_time_str,
            check_out_time_str,
            timesheet.hours_on_site,
        ]
        sheet.append(row)

    # Create a BytesIO object to save the workbook in memory
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    # Create the HTTP response to download the file
    response = HttpResponse(file_stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=timesheets.xlsx'
    return response


from django.contrib.auth import logout

def logout_view(request):
    logout(request)  # This will log out the user
    response = redirect('login')  # Redirect to the login page

    # Prevent the browser from caching the page to avoid back-button navigation
    response['Cache-Control'] = 'no-store'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response
