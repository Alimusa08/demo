# api/utils.py
import re

def normalize_arabic(text: str) -> str:
    if not text:
        return text

    # Normalize Arabic diacritics (tashkeel) — remove them
    text = re.sub(r'[\u0617-\u061A\u064B-\u065F]', '', text)

    # Normalize alef variations → ا
    text = re.sub(r'[أإآ]', 'ا', text)

    # Normalize ya variations → ي
    text = re.sub(r'ى', 'ي', text)

    # Normalize ta marbuta → ه
    text = re.sub(r'ة', 'ه', text)

    # Convert Arabic-Indic numerals to Western → ١٢٣ to 123
    indic = '٠١٢٣٤٥٦٧٨٩'
    for i, d in enumerate(indic):
        text = text.replace(d, str(i))

    return text.strip()