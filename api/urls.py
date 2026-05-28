# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat),
    path("", views.chat_page),
    path("webhook/", views.whatsapp_webhook),
    path("health/", lambda request: JsonResponse({"status": "ok"})),  
]