# api/tool_functions.py
from .models import Appointment, TimeSlot

def check_availability(date, service_type):
    slots = TimeSlot.objects.filter(
        date=date,
        service_type=service_type,
        is_booked=False
    ).values_list("time", flat=True)

    if slots:
        # convert time objects to strings
        return {"available_slots": [str(t) for t in slots]}
    return {"available_slots": [], "message": "No slots available for this date and service."}


def create_appointment(patient_name, phone, date, time, service_type):
    slot = TimeSlot.objects.filter(
        date=date,
        time=time,
        service_type=service_type,
        is_booked=False
    ).first()

    if not slot:
        return {"success": False, "message": "That slot is no longer available, please choose another."}

    appointment = Appointment.objects.create(
        patient_name=patient_name,
        phone=phone,
        slot=slot,
        service_type=service_type
    )
    slot.is_booked = True
    slot.save()

    return {
        "success": True,
        "appointment_id": str(appointment.id),
        "message": f"Appointment booked for {patient_name} on {date} at {time}."
    }


def cancel_appointment(appointment_id):
    try:
        appt = Appointment.objects.get(id=appointment_id)
        appt.slot.is_booked = False
        appt.slot.save()
        appt.delete()
        return {"success": True, "message": "Appointment cancelled successfully."}
    except Appointment.DoesNotExist:
        return {"success": False, "message": "No appointment found with that ID."}


TOOL_FUNCTIONS = {
    "check_availability": check_availability,
    "create_appointment": create_appointment,
    "cancel_appointment": cancel_appointment,
}