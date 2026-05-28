# api/tools.py
BOOKING_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": """Check available slots for a given date and service.
IMPORTANT:
- date must be in YYYY-MM-DD format. Today is injected in the system prompt — calculate correctly.
- service_type must be EXACTLY one of: 'blood test', 'urine test', 'full checkup'
- If the user says فحص دم → 'blood test', فحص بول → 'urine test', فحص كامل → 'full checkup'
- If result is empty, tell the user honestly there are no slots and suggest checking another date. Do NOT retry silently or make up availability.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "service_type": {"type": "string", "enum": ["blood test", "urine test", "full checkup"]}
                },
                "required": ["date", "service_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": """Book an appointment. Only call this after the user explicitly confirms.
IMPORTANT:
- Use the EXACT date and time the user chose — do not guess or change them.
- service_type must be EXACTLY one of: 'blood test', 'urine test', 'full checkup'
- If booking fails, tell the user honestly and ask them to pick another slot.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "phone":        {"type": "string"},
                    "date":         {"type": "string", "description": "YYYY-MM-DD"},
                    "time":         {"type": "string", "description": "HH:MM in 24h format e.g. 13:00"},
                    "service_type": {"type": "string", "enum": ["blood test", "urine test", "full checkup"]}
                },
                "required": ["patient_name", "phone", "date", "time", "service_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"}
                },
                "required": ["appointment_id"]
            }
        }
    }
]