import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LANG_MAP = {
    "Italian": "it",
    "English": "en",
    "Spanish": "es",
    "Spanish; Castilian": "es",
    "French": "fr",
    "German": "de",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese": "zh",
    "Korean": "ko",
    "Swedish": "sv",
    "Norwegian": "no",
    "Danish": "da",
    "Finnish": "fi",
    "Polish": "pl",
    "Czech": "cs",
    "Slovak": "sk",
    "Hungarian": "hu",
    "Romanian": "ro",
    "Bulgarian": "bg",
    "Greek": "el",
    "Turkish": "tr",
    "Arabic": "ar",
    "Hebrew": "he",
    "Persian": "fa",
    "Urdu": "ur",
}

DATA_FOLDER = Path(__file__).parent.parent / "data"

HEADERS = {
    "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
    "x-rapidapi-host": os.getenv("RAPID_API_HOST"),
}
URL = f"https://{os.getenv('RAPID_API_HOST')}"
