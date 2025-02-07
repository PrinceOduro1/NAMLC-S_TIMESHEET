from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login',views.login_view,name='login'),
    path('register/', views.register, name='register'),  # Employee Registration
    path('sign_in/', views.sign_in, name='sign_in'),  # Employee Sign-In
    path('sign_out/', views.sign_out, name='sign_out'),  # Employee Sign-Out
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Admin Panel
    path('get_employee_attendance_data/', views.get_employee_attendance_data, name='get_employee_attendance_data'),
    path('view_timesheet/', views.view_sheet, name='view_timesheet'),
    path('download_timesheets/', views.download_timesheets, name='download_timesheets'),
    path('logout/', views.logout_view, name='logout')

]
