# api/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_service import run_ai_with_tools
import json
import requests
from django.conf import settings
from .models import Conversation


def chat_page(request):
    return render(request, 'chat.html')

@csrf_exempt
def chat(request):
    if request.method == "POST":
        body = json.loads(request.body)
        message = body.get("message", "")
        history = body.get("history", [])

        history.append({"role": "user", "content": message})
        reply, updated_history = run_ai_with_tools(history)

        return JsonResponse({"reply": reply, "history": updated_history})

    return JsonResponse({"status": "ok"})

# api/views.py



def send_whatsapp_message(to: str, message: str):
    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


@csrf_exempt
def whatsapp_webhook(request):

    # ── Verification handshake (Meta calls this once when you set up the webhook)
    if request.method == "GET":
        mode      = request.GET.get("hub.mode")
        token     = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return JsonResponse(int(challenge), safe=False)
        return JsonResponse({"error": "Forbidden"}, status=403)

    # ── Incoming messages
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            # Navigate Meta's nested payload
            entry   = body["entry"][0]
            changes = entry["changes"][0]
            value   = changes["value"]

            # Ignore status updates (delivered, read, etc.)
            if "messages" not in value:
                return JsonResponse({"status": "ignored"})

            message = value["messages"][0]

            # Ignore non-text messages (images, voice notes, etc.)
            if message["type"] != "text":
                send_whatsapp_message(
                    message["from"],
                    "عذراً، بقدر أتعامل مع النصوص بس في الوقت الحالي. 😊"
                )
                return JsonResponse({"status": "ignored"})

            user_phone = message["from"]
            user_text  = message["text"]["body"]

            # Load or create conversation for this user
            convo, _ = Conversation.objects.get_or_create(phone=user_phone)
            history  = convo.history or []

            # Keep last 20 messages to avoid token bloat
            history = history[-20:]

            # Run AI
            history.append({"role": "user", "content": user_text})
            reply, updated_history = run_ai_with_tools(history)

            # Save updated history
            convo.history = updated_history
            convo.save()

            # Send reply back to user
            send_whatsapp_message(user_phone, reply)

            return JsonResponse({"status": "ok"})

        except Exception as e:
            print(f"Webhook error: {e}")
            return JsonResponse({"status": "error"}, status=200)
            # ↑ always return 200 to Meta, otherwise it will keep retrying

    return JsonResponse({"status": "ok"})