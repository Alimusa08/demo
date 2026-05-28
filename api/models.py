from django.db import models

# Create your models here.

class Conversation(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    history = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone


class TimeSlot(models.Model):
    date = models.DateField()
    time = models.TimeField()
    service_type = models.CharField(max_length=100)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} {self.time} - {self.service_type}"


class Appointment(models.Model):
    patient_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.slot}"