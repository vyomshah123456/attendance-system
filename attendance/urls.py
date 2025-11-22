from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_page, name='student_page'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('stats/', views.get_attendance_stats, name='get_stats'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('toggle-attendance/', views.toggle_attendance, name='toggle_attendance'),
    path('toggle-progress/', views.toggle_progress_bar, name='toggle_progress'),
    path('update-strength/', views.update_strength, name='update_strength'),
    path('live-attendance/', views.get_live_attendance, name='live_attendance'),
    path('view-history/', views.view_history, name='view_history'),
    path('download/', views.download_csv, name='download_csv'),
]