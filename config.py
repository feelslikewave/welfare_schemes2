
# ============= config.py =============
"""Configuration Settings"""
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Directories
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create directories
for d in [DATA_DIR, STATIC_DIR / "audio", DATA_DIR / "videos", TEMPLATES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Indian States
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Delhi", "Jammu and Kashmir"
]

# Categories
CATEGORIES = [
    "Agriculture", "Education", "Health", "Housing", "Employment",
    "Social Welfare", "Women and Child", "Financial Inclusion",
    "Rural Development", "Senior Citizens", "Disability Welfare"
]

# Languages
LANGUAGES = {
    "en": "English",
    "hi": "Hindi", 
    "mr": "Marathi",
    "gu": "Gujarati"
}

