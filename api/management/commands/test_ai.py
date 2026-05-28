# bot/management/commands/test_ai.py
from django.core.management.base import BaseCommand
from api.ai_service import run_ai_with_tools
from api.utils import normalize_arabic



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        history = []
        print("Type 'quit' to exit\n")
        while True:
            user_input = normalize_arabic(input("You: "))
            if user_input == "quit":
                break
            history.append({"role": "user", "content": user_input})
            reply, history = run_ai_with_tools(history)  # ← unpack both
            print(f"Bot: {reply}\n")