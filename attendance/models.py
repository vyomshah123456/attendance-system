from django.db import models
from django.utils import timezone


class AttendanceSession(models.Model):
    is_active = models.BooleanField(default=False)
    show_progress = models.BooleanField(default=True)
    total_strength = models.IntegerField(default=60)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance Session"
        verbose_name_plural = "Attendance Session"

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"Session - {status} ({self.date})"

    @classmethod
    def get_session(cls):
        session, created = cls.objects.get_or_create(pk=1)
        today = timezone.now().date()
        if session.date != today:
            session.date = today
            session.is_active = False
            session.save()
            AttendanceRecord.objects.all().delete()
        return session


class AttendanceRecord(models.Model):
    roll_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        unique_together = ['roll_number', 'date']

    def __str__(self):
        return f"{self.roll_number} - {self.timestamp.strftime('%I:%M %p')}"