"""
summarizer.py - Sahayta AI Scheme Summarizer
Place this file inside: welfare_schemes/services/summarizer.py

Summarizes government scheme details and translates the summary
into the user's preferred language automatically.

Dependencies:
    pip install transformers torch deep-translator sentencepiece
"""

from transformers import pipeline
from deep_translator import GoogleTranslator
import re


# ─────────────────────────────────────────────
# LANGUAGE CONFIGURATIONS
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

# Summary length presets (in words, approximately)
SUMMARY_PRESETS = {
    "short":  {"max_length": 80,  "min_length": 30},   # ~2 lines
    "medium": {"max_length": 150, "min_length": 60},   # ~4 lines
    "long":   {"max_length": 250, "min_length": 100},  # ~6 lines
}


# ─────────────────────────────────────────────
# MAIN SUMMARIZER CLASS
# ─────────────────────────────────────────────

class SchemeSummarizer:
    """
    Summarizes government scheme text and translates the result
    into the user's selected language.

    Usage:
        from services.summarizer import SchemeSummarizer

        summarizer = SchemeSummarizer(language="hi")
        summary = summarizer.summarize(scheme_text)

        # Or translate after setting language
        summarizer.set_language("ta")
        summary = summarizer.summarize_scheme(scheme_dict)
    """

    def __init__(self, language: str = "en", summary_length: str = "medium"):
        """
        Args:
            language       : Language code for output (e.g. 'hi', 'ta', 'gu').
            summary_length : 'short', 'medium', or 'long'.
        """
        self.language = language if language in SUPPORTED_LANGUAGES else "en"
        self.summary_length = summary_length if summary_length in SUMMARY_PRESETS else "medium"
        self._summarizer = None
        self._load_model()

    # ── Model Loading ─────────────────────────

    def _load_model(self):
        """Load the BART summarization model. Falls back gracefully if unavailable."""
        try:
            print("[Sahayta] Loading summarization model... (first run may take time)")
            self._summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                truncation=True
            )
            print("[Sahayta] Summarization model loaded successfully.")
        except Exception as e:
            print(f"[Sahayta] AI model unavailable ({e}). Using extractive summarizer.")
            self._summarizer = None

    # ── Language Control ──────────────────────

    def set_language(self, lang_code: str) -> bool:
        """Change the output language dynamically."""
        if lang_code not in SUPPORTED_LANGUAGES:
            print(f"[Sahayta] '{lang_code}' not supported. Keeping '{self.language}'.")
            return False
        self.language = lang_code
        print(f"[Sahayta] Summarizer language set to: {SUPPORTED_LANGUAGES[lang_code]}")
        return True

    def set_summary_length(self, length: str):
        """Change summary length: 'short', 'medium', or 'long'."""
        if length in SUMMARY_PRESETS:
            self.summary_length = length

    # ── Core Summarization ────────────────────

    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace, special characters, and normalize text."""
        text = re.sub(r'\s+', ' ', text)          # collapse whitespace
        text = re.sub(r'[*_~`#]', '', text)        # remove markdown symbols
        text = re.sub(r'http\S+', '', text)         # remove URLs
        return text.strip()

    def _extractive_summary(self, text: str, num_sentences: int = 3) -> str:
        """
        Fallback: Extract the most important sentences without AI model.
        Prioritizes sentences with keywords related to schemes/benefits.
        """
        sentences = [s.strip() for s in re.split(r'[.।|]\s*', text) if len(s.strip()) > 20]

        if not sentences:
            return text[:300] + "..."

        # Score sentences by keyword relevance
        keywords = [
            "benefit", "eligibility", "apply", "amount", "rupee", "rs.", "lakh",
            "crore", "scheme", "yojana", "government", "provide", "support",
            "farmer", "woman", "student", "pension", "loan", "subsidy", "free"
        ]

        def score(sentence):
            s = sentence.lower()
            return sum(1 for kw in keywords if kw in s)

        scored = sorted(enumerate(sentences), key=lambda x: score(x[1]), reverse=True)
        top_indices = sorted([i for i, _ in scored[:num_sentences]])
        selected = [sentences[i] for i in top_indices]
        return ". ".join(selected) + "."

    def _ai_summary(self, text: str) -> str:
        """Use BART model to generate an abstractive summary in English."""
        preset = SUMMARY_PRESETS[self.summary_length]
        # BART supports max 1024 tokens input
        truncated = text[:1024]
        try:
            result = self._summarizer(
                truncated,
                max_length=preset["max_length"],
                min_length=preset["min_length"],
                do_sample=False,
                truncation=True
            )
            return result[0]["summary_text"]
        except Exception as e:
            print(f"[Sahayta] AI summarization failed: {e}. Falling back to extractive.")
            return self._extractive_summary(text)

    def _translate(self, text: str, target_lang: str) -> str:
        """Translate English text to target language."""
        if target_lang == "en":
            return text
        try:
            return GoogleTranslator(source="en", target=target_lang).translate(text)
        except Exception as e:
            print(f"[Sahayta] Translation error: {e}. Returning English summary.")
            return text

    # ── Public API ────────────────────────────

    def summarize(self, text: str, language: str = None) -> str:
        """
        Summarize a plain text string and translate to user language.

        Args:
            text     : Raw English text describing a scheme.
            language : Override output language for this call only.

        Returns:
            Summarized and translated string.
        """
        if not text or not isinstance(text, str):
            return ""

        target_lang = language if language in SUPPORTED_LANGUAGES else self.language
        cleaned = self._clean_text(text)

        # Use AI model only if text is long enough and model is available
        if self._summarizer and len(cleaned.split()) > 60:
            english_summary = self._ai_summary(cleaned)
        else:
            num = {"short": 2, "medium": 3, "long": 5}[self.summary_length]
            english_summary = self._extractive_summary(cleaned, num_sentences=num)

        return self._translate(english_summary, target_lang)

    def summarize_scheme(self, scheme: dict, language: str = None) -> dict:
        """
        Summarize and translate a full scheme dictionary.

        Generates a 'summary' field from available text fields and
        translates name, description, benefits, and eligibility.

        Args:
            scheme   : Dict with keys like name, description, benefits, eligibility.
            language : Override output language for this call only.

        Returns:
            New dict with translated fields and a 'summary' key added.
        """
        target_lang = language if language in SUPPORTED_LANGUAGES else self.language

        # Build combined text for summarization
        parts = []
        for field in ["description", "benefits", "eligibility", "how_to_apply"]:
            if scheme.get(field):
                parts.append(scheme[field])
        full_text = " ".join(parts)

        result = scheme.copy()

        # Add AI/extractive summary
        result["summary"] = self.summarize(full_text, target_lang)

        # Translate individual fields too
        translate_fields = ["name", "description", "benefits", "eligibility", "how_to_apply", "category"]
        for field in translate_fields:
            if result.get(field) and isinstance(result[field], str):
                result[field] = self._translate(result[field], target_lang)

        result["language"] = SUPPORTED_LANGUAGES.get(target_lang, "English")
        return result

    def summarize_list_of_schemes(self, schemes: list, language: str = None) -> list:
        """
        Summarize and translate a list of scheme dictionaries.

        Args:
            schemes  : List of scheme dicts.
            language : Override output language for all schemes.

        Returns:
            List of summarized and translated scheme dicts.
        """
        return [self.summarize_scheme(s, language) for s in schemes]

    def summarize_for_card(self, scheme: dict, language: str = None) -> str:
        """
        Generate a short 2-line summary suitable for a scheme card/tile in the UI.

        Args:
            scheme   : Scheme dictionary.
            language : Output language code.

        Returns:
            Short translated summary string.
        """
        original_length = self.summary_length
        self.summary_length = "short"
        text = scheme.get("description", "") or scheme.get("benefits", "")
        result = self.summarize(text, language)
        self.summary_length = original_length
        return result


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json

    summarizer = SchemeSummarizer(language="hi", summary_length="medium")

    scheme = {
        "name": "PM Kisan Samman Nidhi",
        "category": "Agriculture",
        "description": (
            "The Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a central sector scheme "
            "launched by the Government of India to provide income support to all landholding "
            "farmers' families across the country to supplement their financial needs for "
            "procuring various inputs related to agriculture and allied activities as well as "
            "domestic needs."
        ),
        "benefits": (
            "Under this scheme, financial benefit of Rs. 6000 per year is provided to eligible "
            "farmer families, payable in three equal instalments of Rs. 2000 each every four months. "
            "The amount is directly transferred to the bank accounts of the beneficiaries."
        ),
        "eligibility": (
            "All landholding farmers' families, which have cultivable land holding in their names "
            "are eligible. Farmer families belonging to higher economic strata are excluded, including "
            "constitutional post holders, current or former government employees, income tax payers, "
            "and professionals like doctors, engineers, and lawyers."
        ),
        "how_to_apply": (
            "Farmers can register through the PM-KISAN portal, Common Service Centres (CSC), "
            "or through the local revenue or agriculture department."
        )
    }

    print("=== Sahayta AI - Summarizer Test ===\n")

    # Test 1: Hindi summary
    summarizer.set_language("hi")
    result = summarizer.summarize_scheme(scheme)
    print(f"[Hindi Summary]\n{result['summary']}\n")

    # Test 2: Tamil card summary
    card = summarizer.summarize_for_card(scheme, language="ta")
    print(f"[Tamil Card]\n{card}\n")

    # Test 3: Gujarati full scheme
    summarizer.set_language("gu")
    full = summarizer.summarize_scheme(scheme)
    print(f"[Gujarati Full]\n{json.dumps(full, ensure_ascii=False, indent=2)}")