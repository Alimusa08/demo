# bot/ai_service.py
import os
from litellm import completion
from django.conf import settings
from .tools import BOOKING_TOOLS
from .tool_functions import TOOL_FUNCTIONS
from datetime import date, timedelta
import time

os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY



tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

SYSTEM_PROMPT = f"""
أنت مساعد ذكي لمختبر طبي. بتساعد العملاء يحجزوا مواعيد أو يسألوا عن الأوقات المتاحة أو يلغوا الحجوزات.
تكلم دايمًا باللهجة المصرية العامية وكن ودود وبسيط.

التواريخ:
- النهارده: {date.today().strftime("%Y-%m-%d")}
- بكرا: {tomorrow}
- لما المريض يقول "بكرا" استخدم {tomorrow} بالظبط.

الخدمات المتاحة:
- فحص دم → blood test
- فحص بول → urine test  
- فحص كامل → full checkup

قواعد صارمة:
1. اتحقق من الأوقات الأول قبل ما تطلب بيانات المريض.
2. لما تبعت طلب للأداة، استخدم التاريخ بصيغة YYYY-MM-DD والوقت بصيغة HH:MM.
3. لو مفيش أوقات متاحة، قول للمريض بصراحة وأسأله يجرب تاريخ تاني — متكدبش أو تتجاهل.
4. متحجزش غير لما يكون عندك: الاسم، التليفون، التاريخ، الوقت، نوع الخدمة — كلهم متأكدين من المريض.
5. بعد ما تجمع كل البيانات، لخصها واسأل "تأكد الحجز؟" — وبس بعد ما يقول أيوه، اعمل الحجز.
6. بعد الحجز، قول للمريض رقم الحجز والتفاصيل — ومتبقاش تعمل أي طلب للأداة تاني.
"""
# api/ai_service.py

def serialize_message(msg):
    if isinstance(msg, dict):
        return msg
    # Convert LiteLLM/OpenAI Message object to plain dict
    result = {"role": msg.role, "content": msg.content or ""}
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        result["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in msg.tool_calls
        ]
    return result

def run_ai_with_tools(conversation_history: list) -> tuple[str, list]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    import json
    while True:
        try:
            response = completion(
                model="groq/llama-3.3-70b-versatile",
                messages=messages,
                tools=BOOKING_TOOLS,
                temperature=0.2,
            )
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                print("Rate limit, waiting 15s...")
                time.sleep(15)
                continue
            raise e

        choice = response.choices[0]

        if choice.finish_reason == "stop":
            updated_history = [serialize_message(m) for m in messages[1:]]
            updated_history.append({"role": "assistant", "content": choice.message.content})
            return choice.message.content, updated_history

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)  # LiteLLM object — fine for the loop

            for tool_call in choice.message.tool_calls:
                fn = TOOL_FUNCTIONS.get(tool_call.function.name)
                args = json.loads(tool_call.function.arguments)
                result = fn(**args) if fn else {"error": "Unknown tool"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })