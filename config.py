"""Velocity Vietnamese - language pack, brand and motion design constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_DIR = BASE_DIR / "output"
LESSONS_DIR = OUTPUT_DIR / "lessons"
HISTORY_DIR = OUTPUT_DIR / "history"
SCENE_DIR = BASE_DIR / "scene"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# ---------------------------------------------------------------- brand

BRAND = "VELOCITY VIETNAMESE"
BRAND_LOCKUP_TOP = "VELOCITY"
BRAND_LOCKUP_BOTTOM = "VIETNAMESE"
HANDLE = "@velocityvietnamese"
MASCOT_NAME = "Velo"

LANGUAGE = {
    "code": "vi",
    "name": "Vietnamese",
    "native_name": "Tiếng Việt",
    "english_voice": "en-US-AvaNeural",
    "english_fallback_voice": "en-US-GuyNeural",
    "native_voice": "vi-VN-HoaiMyNeural",
    "native_fallback_voice": "vi-VN-NamMinhNeural",
    "english_rate": "-2%",
    "native_rate": "-6%",
    "english_pitch": "+0Hz",
    "native_pitch": "+0Hz",
    "native_label": "TIẾNG VIỆT",
    "translit_label": "SAY IT LIKE",
    "greeting": "Xin chào!",
    "encouragement": "Tuyệt vời!",
}

AI_MODEL = os.getenv("AI_MODEL", "gemini-fast")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# ---------------------------------------------------------------- timing (seconds)

INTRO_DURATION = 4.0
OUTRO_DURATION = 5.2
EN_CARD_IN = 0.55
GAP_EN_NATIVE = 0.5
NATIVE_CARD_LEAD = 0.35
GAP_BEFORE_REPEAT = 0.8
TAIL_HOLD = 1.4

# ---------------------------------------------------------------- palette

INK = "#3C3C3C"
MUTED = "#8A8A8A"
CREAM = "#FFF8E7"
GREEN = "#58CC02"
GREEN_DARK = "#46A302"
GREEN_DEEP = "#3D8F00"
BLUE = "#1CB0F6"
PURPLE = "#A560E8"
ORANGE = "#FF7A00"
RED = "#FF4B4B"
YELLOW = "#F5A700"
TEAL = "#00A889"
PINK = "#E056A0"

PALETTE = [GREEN, BLUE, PURPLE, ORANGE, RED, YELLOW, TEAL, PINK]

# ---------------------------------------------------------------- categories
# (english, vietnamese, icon, accent)

CATEGORY_TABLE = [
    ("Greetings", "Lời Chào", "hand", BLUE),
    ("Basic Phrases", "Cụm Từ Cơ Bản", "chat", GREEN),
    ("Common Expressions", "Biểu Hiện Thông Thường", "chat", BLUE),
    ("Travel", "Du Lịch", "plane", BLUE),
    ("Restaurant", "Nhà Hàng", "fork", ORANGE),
    ("Shopping", "Mua Sắm", "bag", PINK),
    ("Emergency", "Khẩn Cấp", "siren", RED),
    ("Family Terms", "Từ Gia Đình", "heart", PINK),
    ("Numbers", "Số", "hash", PURPLE),
    ("Time", "Thời Gian", "clock", TEAL),
    ("Motivation", "Động Lực", "rocket", PURPLE),
    ("Love", "Tình Yêu", "heart", RED),
    ("Success", "Thành Công", "trophy", YELLOW),
    ("Wisdom", "Trí Tuệ", "book", PURPLE),
    ("Happiness", "Hạnh Phúc", "smile", YELLOW),
    ("Self Improvement", "Tự Cải Thiện", "leaf", GREEN),
    ("Gratitude", "Lòng Biết Ơn", "heart", ORANGE),
    ("Friendship", "Tình Bạn", "users", TEAL),
    ("Hope", "Hy Vọng", "sun", ORANGE),
    ("Creativity", "Sáng Tạo", "palette", PINK),
    ("Inner Peace", "Bình An Nội Tâm", "lotus", TEAL),
    ("Confidence", "Tự Tin", "shield", BLUE),
    ("Perseverance", "Kiên Trì", "mountain", ORANGE),
    ("Inspiration", "Cảm Hứng", "sparkles", PURPLE),
    ("Positive Life", "Cuộc Sống Tích Cực", "sun", GREEN),
    ("Courage", "Can Đảm", "shield", RED),
    ("Kindness", "Tử Tế", "heart", PINK),
    ("Patience", "Kiên Nhẫn", "hourglass", TEAL),
    ("Forgiveness", "Tha Thứ", "hands", ORANGE),
    ("Strength", "Sức Mạnh", "dumbbell", RED),
    ("Joy", "Niềm Vui", "smile", YELLOW),
    ("Balance", "Cân Bằng", "scale", TEAL),
    ("Growth", "Phát Triển", "sprout", GREEN),
    ("Purpose", "Mục Đích", "target", PURPLE),
    ("Mindfulness", "Chánh Niệm", "lotus", TEAL),
    ("Daily Routine", "Thói Quen Hàng Ngày", "calendar", BLUE),
    ("Weather", "Thời Tiết", "cloud", BLUE),
    ("Feelings", "Cảm Xúc", "smile", PINK),
    ("Food", "Đồ Ăn", "fork", ORANGE),
    ("Health", "Sức Khỏe", "heart", GREEN),
    ("Work", "Công Việc", "briefcase", BLUE),
    ("Technology", "Công Nghệ", "chip", PURPLE),
    ("Nature", "Thiên Nhiên", "leaf", GREEN),
    ("Animals", "Động Vật", "paw", ORANGE),
    ("Colors", "Màu Sắc", "palette", PINK),
    ("Directions", "Chỉ Đường", "compass", BLUE),
    ("Body Parts", "Bộ Phận Cơ Thể", "hand", TEAL),
    ("Clothes", "Quần Áo", "shirt", PINK),
    ("Music", "Âm Nhạc", "music", PURPLE),
    ("Sports", "Thể Thao", "ball", ORANGE),
    ("Holidays", "Ngày Lễ", "gift", RED),
    ("Education", "Giáo Dục", "book", BLUE),
    ("Culture", "Văn Hóa", "globe", TEAL),
    ("Finance", "Tài Chính", "coin", GREEN),
    ("Relationships", "Mối Quan Hệ", "users", PINK),
]

CATEGORIES = [c[0] for c in CATEGORY_TABLE]
CATEGORIES_NATIVE = {c[0]: c[1] for c in CATEGORY_TABLE}
CATEGORY_META = {c[0]: {"native": c[1], "icon": c[2], "accent": c[3]} for c in CATEGORY_TABLE}
MAX_RECENT_CATEGORIES = 25

HASHTAGS = [
    "#learnvietnamese",
    "#vietnameselessons",
    "#vietnameseforbeginners",
    "#languagelearning",
    "#vietnamesevocabulary",
    "#velocityvietnamese",
    "#dailyvietnamese",
    "#vietnamese",
    "#learnlanguages",
    "#speakvietnamese",
    "#bilingual",
    "#languagetips",
]
