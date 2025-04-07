from django.urls import path,re_path
from . import views
from django.shortcuts import render
from django.http import HttpResponseNotFound

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

handler404 = 'nguvu_timesheet.urls.custom_404'

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
    path('logout/', views.logout_view, name='logout'),
    path('reset-password',views.reset_password,name='reset-password'),
    path('get_email_reset?password',views.get_email,name='get_email'),
    path('check-email/', views.check_email_exists, name='check_email_exists'),
    path('register-face/', views.register_face, name='register-face'),
    path('face-sign-in/', views.face_sign_in, name='face_sign_in'),
    path('face-sign-out/', views.face_sign_out, name='face_sign_out'),

]
