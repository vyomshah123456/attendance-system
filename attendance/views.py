from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import AttendanceSession, AttendanceRecord
import csv
from datetime import datetime


def student_page(request):
    session = AttendanceSession.get_session()
    context = {
        'is_active': session.is_active,
        'show_progress': session.show_progress,
        'total_strength': session.total_strength,
    }
    return render(request, 'student_page.html', context)


def mark_attendance(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number', '').strip().upper()
        if not roll_number:
            return JsonResponse({'success': False, 'message': 'Please enter your roll number!'})
        session = AttendanceSession.get_session()
        if not session.is_active:
            return JsonResponse({'success': False, 'message': 'Attendance is not started yet. Please wait for admin to enable it.'})
        today = timezone.now().date()
        if AttendanceRecord.objects.filter(roll_number=roll_number, date=today).exists():
            return JsonResponse({'success': False, 'message': f'Roll Number {roll_number} has already marked attendance today!'})
        try:
            AttendanceRecord.objects.create(roll_number=roll_number, date=today)
            current_count = AttendanceRecord.objects.filter(date=today).count()
            return JsonResponse({'success': True, 'message': f'Attendance marked successfully for {roll_number}!', 'current_count': current_count, 'total_strength': session.total_strength})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_attendance_stats(request):
    session = AttendanceSession.get_session()
    today = timezone.now().date()
    current_count = AttendanceRecord.objects.filter(date=today).count()
    return JsonResponse({'current_count': current_count, 'total_strength': session.total_strength, 'is_active': session.is_active, 'show_progress': session.show_progress})


def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid username or password!'})
    return render(request, 'admin_login.html')


@login_required(login_url='/admin-login/')
def admin_dashboard(request):
    session = AttendanceSession.get_session()
    today = timezone.now().date()
    records = AttendanceRecord.objects.filter(date=today)
    current_count = records.count()
    context = {'session': session, 'records': records, 'current_count': current_count, 'total_strength': session.total_strength}
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='/admin-login/')
def toggle_attendance(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        session = AttendanceSession.get_session()
        if action == 'start':
            session.is_active = True
            message = 'Attendance started successfully!'
        elif action == 'stop':
            session.is_active = False
            message = 'Attendance stopped successfully!'
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'})
        session.save()
        return JsonResponse({'success': True, 'message': message, 'is_active': session.is_active})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='/admin-login/')
def toggle_progress_bar(request):
    if request.method == 'POST':
        session = AttendanceSession.get_session()
        session.show_progress = not session.show_progress
        session.save()
        return JsonResponse({'success': True, 'show_progress': session.show_progress, 'message': f"Progress bar {'shown' if session.show_progress else 'hidden'} for students"})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='/admin-login/')
def update_strength(request):
    if request.method == 'POST':
        try:
            strength = int(request.POST.get('strength', 60))
            if strength < 1:
                raise ValueError
            session = AttendanceSession.get_session()
            session.total_strength = strength
            session.save()
            return JsonResponse({'success': True, 'message': f'Total strength updated to {strength}'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Please enter a valid number'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='/admin-login/')
def get_live_attendance(request):
    today = timezone.now().date()
    records = AttendanceRecord.objects.filter(date=today)
    data = [{'roll_number': record.roll_number, 'time': record.timestamp.strftime('%I:%M %p')} for record in records]
    return JsonResponse({'records': data, 'count': len(data)})


@login_required(login_url='/admin-login/')
def view_history(request):
    date_str = request.GET.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        records = AttendanceRecord.objects.filter(date=date)
        data = [{'roll_number': record.roll_number, 'time': record.timestamp.strftime('%I:%M %p')} for record in records]
        return JsonResponse({'success': True, 'records': data, 'count': len(data), 'date': date.strftime('%B %d, %Y')})
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid date format'})


@login_required(login_url='/admin-login/')
def download_csv(request):
    date_str = request.GET.get('date', '')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = timezone.now().date()
    else:
        date = timezone.now().date()
    records = AttendanceRecord.objects.filter(date=date)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{date}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Roll Number', 'Date', 'Time'])
    for record in records:
        writer.writerow([record.roll_number, record.date.strftime('%Y-%m-%d'), record.timestamp.strftime('%I:%M %p')])
    return response


@login_required(login_url='/admin-login/')
def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')