# from google.cloud import translate_v2 as translate

# class MultilingualTranslator:
#     def __init__(self):
#         self.client = translate.Client()

#     def translate_text(self, text, target_language="hi"):
#         if not text:
#             return text
        
#         result = self.client.translate(
#             text,
#             target_language=target_language
#         )
        
#         return result["translatedText"]




"""
translator.py - Sahayta AI Language Translator Module
Place this file inside: welfare_schemes/services/translator.py

Handles dynamic language translation for the website based on user preferences.
Supports major Indian languages for government scheme accessibility.
"""

from deep_translator import GoogleTranslator
import json
import os

# ─────────────────────────────────────────────
# SUPPORTED LANGUAGES
# ─────────────────────────────────────────────

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "bn": "Bengali (বাংলা)",
    "te": "Telugu (తెలుగు)",
    "mr": "Marathi (मराठी)",
    "ta": "Tamil (தமிழ்)",
    "gu": "Gujarati (ગુજરાતી)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "or": "Odia (ଓଡ଼ିଆ)",
    "as": "Assamese (অসমীয়া)",
    "ur": "Urdu (اردو)",
}

STATE_LANGUAGE_MAP = {
    "Andhra Pradesh": "te", "Arunachal Pradesh": "en", "Assam": "as",
    "Bihar": "hi", "Chhattisgarh": "hi", "Goa": "en", "Gujarat": "gu",
    "Haryana": "hi", "Himachal Pradesh": "hi", "Jharkhand": "hi",
    "Karnataka": "kn", "Kerala": "ml", "Madhya Pradesh": "hi",
    "Maharashtra": "mr", "Manipur": "en", "Meghalaya": "en",
    "Mizoram": "en", "Nagaland": "en", "Odisha": "or", "Punjab": "pa",
    "Rajasthan": "hi", "Sikkim": "en", "Tamil Nadu": "ta",
    "Telangana": "te", "Tripura": "bn", "Uttar Pradesh": "hi",
    "Uttarakhand": "hi", "West Bengal": "bn", "Delhi": "hi",
    "Jammu & Kashmir": "ur", "Ladakh": "hi", "Puducherry": "ta",
    "Chandigarh": "pa",
}

CACHE_FILE = "translation_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


class MultilingualTranslator:
    """
    Main translator class for Sahayta AI.

    Usage:
        from services.translator import MultilingualTranslator
        translator = MultilingualTranslator()
        translator.set_language("hi")
        print(translator.translate("Welcome to Sahayta AI"))
    """

    def __init__(self):
        self.cache = load_cache()
        self.current_language = "en"

    def set_language(self, lang_code: str) -> bool:
        """Set active language by code (e.g. 'hi', 'ta', 'gu')."""
        if lang_code not in SUPPORTED_LANGUAGES:
            print(f"[Sahayta] '{lang_code}' not supported. Defaulting to English.")
            self.current_language = "en"
            return False
        self.current_language = lang_code
        print(f"[Sahayta] Language set to: {SUPPORTED_LANGUAGES[lang_code]}")
        return True

    def set_language_by_state(self, state_name: str) -> str:
        """Auto-set language based on the user's selected Indian state."""
        lang_code = STATE_LANGUAGE_MAP.get(state_name, "en")
        self.set_language(lang_code)
        return lang_code

    def get_current_language(self) -> dict:
        return {
            "code": self.current_language,
            "name": SUPPORTED_LANGUAGES.get(self.current_language, "English")
        }

    def get_language_options(self) -> list:
        return [{"code": c, "name": n} for c, n in SUPPORTED_LANGUAGES.items()]

    def translate(self, text: str, target_lang: str = None, source_lang: str = "en") -> str:
        """Translate a single text string to the target language."""
        if not text or not isinstance(text, str):
            return text

        if target_lang is None:
            target_lang = self.current_language

        if target_lang == source_lang or target_lang == "en":
            return text

        cache_key = f"{source_lang}__{target_lang}__{text}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            result = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            self.cache[cache_key] = result
            save_cache(self.cache)
            return result
        except Exception as e:
            print(f"[Sahayta] Translation error: {e}")
            return text

    def translate_page_content(self, content_dict: dict, target_lang: str = None) -> dict:
        """Translate a full dictionary of UI text strings."""
        if target_lang is None:
            target_lang = self.current_language

        translated = {}
        for key, value in content_dict.items():
            if isinstance(value, str):
                translated[key] = self.translate(value, target_lang)
            elif isinstance(value, list):
                translated[key] = [
                    self.translate(i, target_lang) if isinstance(i, str) else i
                    for i in value
                ]
            else:
                translated[key] = value
        return translated

    def translate_scheme(self, scheme: dict, target_lang: str = None) -> dict:
        """Translate a government scheme details dictionary."""
        if target_lang is None:
            target_lang = self.current_language

        fields = ["name", "description", "benefits", "eligibility", "how_to_apply", "category"]
        result = scheme.copy()
        for field in fields:
            if field in scheme and isinstance(scheme[field], str):
                result[field] = self.translate(scheme[field], target_lang)
        return result

    def translate_list_of_schemes(self, schemes: list, target_lang: str = None) -> list:
        """Translate a list of scheme dictionaries."""
        return [self.translate_scheme(s, target_lang) for s in schemes]


# Alias for backward compatibility
SahaytaTranslator = MultilingualTranslator


if __name__ == "__main__":
    t = MultilingualTranslator()
    t.set_language("hi")
    print("Hindi:", t.translate("Welcome to Sahayta AI"))