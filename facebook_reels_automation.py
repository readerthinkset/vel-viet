"""
Facebook Reels Automation - Bilingual English/Vietnamese Content Generator
IMPROVED VERSION: Better backgrounds, English categories, no repeats, VELOCITY VIETNAMESE branding
Rounded container style from Habla Verse
"""

import os
import sys
import json
import random
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

if not AI_MODEL:
    raise ValueError(
        "AI_MODEL not set! Please add 'AI_MODEL=gemini-fast' to your .env file. "
        "For GitHub Actions: Add AI_MODEL to repository secrets."
    )

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"

for d in [OUTPUT_DIR, IMAGES_DIR, AUDIO_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

CATEGORIES_ENGLISH = [
    "Greetings",
    "Basic Phrases",
    "Common Expressions",
    "Travel",
    "Restaurant",
    "Shopping",
    "Emergency",
    "Family Terms",
    "Numbers",
    "Time",
    "Motivation",
    "Love",
    "Success",
    "Wisdom",
    "Happiness",
    "Self Improvement",
    "Gratitude",
    "Friendship",
    "Hope",
    "Creativity",
    "Inner Peace",
    "Confidence",
    "Perseverance",
    "Inspiration",
    "Positive Life",
    "Courage",
    "Kindness",
    "Patience",
    "Forgiveness",
    "Strength",
    "Joy",
    "Balance",
    "Growth",
    "Purpose",
    "Mindfulness"

    "Daily Routine",
    "Weather",
    "Feelings",
    "Food",
    "Health",
    "Work",
    "Technology",
    "Nature",
    "Animals",
    "Colors",
    "Directions",
    "Body Parts",
    "Clothes",
    "Music",
    "Sports",
    "Holidays",
    "Education",
    "Culture",
    "Finance",
    "Relationships",]

CATEGORIES_NATIVE = {
    "Greetings": "Lời Chào",
    "Basic Phrases": "Cụm Từ Cơ Bản",
    "Common Expressions": "Biểu Hiện Thông Thường",
    "Travel": "Du Lịch",
    "Restaurant": "Nhà Hàng",
    "Shopping": "Mua Sắm",
    "Emergency": "Khẩn Cấp",
    "Family Terms": "Từ Gia Đình",
    "Numbers": "Số",
    "Time": "Thời Gian",
    "Motivation": "Động Lực",
    "Love": "Tình Yêu",
    "Success": "Thành Công",
    "Wisdom": "Trí Tuệ",
    "Happiness": "Hạnh Phúc",
    "Self Improvement": "Tự Cải Thiện",
    "Gratitude": "Lòng Biết Ơn",
    "Friendship": "Tình Bạn",
    "Hope": "Hy Vọng",
    "Creativity": "Sáng Tạo",
    "Inner Peace": "Bình An Nội Tâm",
    "Confidence": "Tự Tin",
    "Perseverance": "Kiên Trì",
    "Inspiration": "Cảm Hứng",
    "Positive Life": "Cuộc Sống Tích Cực",
    "Courage": "Can Đảm",
    "Kindness": "Tử Tế",
    "Patience": "Kiên Nhẫn",
    "Forgiveness": "Tha Thứ",
    "Strength": "Sức Mạnh",
    "Joy": "Niềm Vui",
    "Balance": "Cân Bằng",
    "Growth": "Phát Triển",
    "Purpose": "Mục Đích",
    "Mindfulness": "Chánh Niệm"
}

ENGLISH_VOICE = "en-US-GuyNeural"
NATIVE_VOICE = "vi-VN-NamMinhNeural"

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"
MAX_RECENT_CATEGORIES = 25


def load_phrase_history():
    if PHRASE_HISTORY_FILE.exists():
        with open(PHRASE_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"phrases": [], "last_updated": None}


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(PHRASE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_phrase_used(english_phrase):
    history = load_phrase_history()
    english_lower = english_phrase.lower().strip()
    for p in history.get("phrases", []):
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    lang_key = "vietnamese"
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            lang_key: phrase[lang_key],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat()
        })
    save_phrase_history(history)
    print(f"[history] Added {len(phrases)} phrases to history (total: {len(history['phrases'])})")


def load_recent_categories():
    if RECENT_CATEGORIES_FILE.exists():
        with open(RECENT_CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"recent_categories": [], "last_updated": None}


def save_recent_categories(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(RECENT_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_available_category():
    recent_data = load_recent_categories()
    recent = recent_data.get("recent_categories", [])
    available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent]
    if not available:
        recent_data["recent_categories"] = recent[-5:]
        save_recent_categories(recent_data)
        available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent_data["recent_categories"]]
        print(f"[rotation] All categories used recently - cleared old ones, {len(available)} available")
    selected = random.choice(available)
    recent.append(selected)
    if len(recent) > MAX_RECENT_CATEGORIES:
        recent = recent[-MAX_RECENT_CATEGORIES:]
    recent_data["recent_categories"] = recent
    save_recent_categories(recent_data)
    print(f"[rotation] Selected '{selected}' ({len(available)} available, {len(recent)} in recent history)")
    return selected


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE[category_english]
    max_attempts = 3

    history = load_phrase_history()
    recent_english = [p["english"] for p in history.get("phrases", []) if p.get("category") == category_english][-30:]

    for attempt in range(max_attempts):
        try:
            import requests
            url = "https://gen.pollinations.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
                "Content-Type": "application/json"
            }

            avoid_text = ""
            if recent_english:
                avoid_text = "\nABSOLUTELY AVOID these already-used phrases:\n" + "\n".join(f"- {p}" for p in recent_english)

            prompt = f"""Create {num_phrases * 6} unique and creative {category_english} phrases for English speakers learning Vietnamese.{avoid_text}

IMPORTANT RULES FOR NATURAL SPEECH:
1. Keep phrases SHORT (5-12 words max per language)
2. Add NATURAL PAUSES using commas (e.g., "Dream big, start small")
3. Use punctuation for breathing room in TTS
4. Avoid long run-on sentences
5. Each phrase should be speakable in 3-5 seconds
6. Vietnamese text should be CLEAN - use standard Vietnamese script
7. Do NOT include multiple versions or slashes - just ONE clean Vietnamese translation
8. Transliteration should be in Roman script for pronunciation
9. BE CREATIVE AND VARIED - do NOT repeat themes from the avoid list

For each phrase:
1. English phrase (with commas for natural pauses)
2. Vietnamese translation (in Vietnamese script)
3. Transliteration (Roman script pronunciation)

Return as JSON array:
[{{"english": "...", "vietnamese": "...", "transliteration": "..."}}]

IMPORTANT: Create FRESH, UNIQUE phrases that haven't been used before.
IMPORTANT: Vietnamese text must be clean - no slashes, no multiple versions."""

            payload = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a Vietnamese teacher. Create short, natural phrases with pauses. Each generation must produce completely different, creative phrases."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": min(0.95 + attempt * 0.03, 1.0)
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            phrases = json.loads(content)

            for p in phrases:
                if "transliteration" not in p and "romaji" in p:
                    p["transliteration"] = p.pop("romaji")
                if "vietnamese" not in p:
                    alt_keys = ["vietnamese_text", "native", "translation", p.get("language", "")]
                    for k in alt_keys:
                        if k in p:
                            p["vietnamese"] = p.pop(k)
                            break
                if "vietnamese" not in p:
                    continue

            unique_phrases = []
            for phrase in phrases:
                if len(phrase["english"].split()) > 15:
                    continue
                if not is_phrase_used(phrase["english"]):
                    unique_phrases.append(phrase)
                if len(unique_phrases) >= num_phrases:
                    break

            if len(unique_phrases) >= num_phrases:
                add_phrases_to_history(unique_phrases[:num_phrases], category_english)
                return unique_phrases[:num_phrases]

            print(f"[content] Attempt {attempt + 1}: API returned {len(phrases)} phrases, only {len(unique_phrases)} are new (need {num_phrases})")
            for p in unique_phrases:
                if p["english"] not in recent_english:
                    recent_english.append(p["english"])

        except Exception as e:
            print(f"[content] Attempt {attempt + 1} failed: {e}")

    print("[content] Using fallback phrases...")
    return get_fresh_fallback_phrases(category_english, num_phrases)



def get_fresh_fallback_phrases(category: str, num_phrases: int) -> list:
    """Return simple English fallback phrases when AI generation fails"""
    generic_fallbacks = [
        {"english": "Hello, nice to meet you.", "vietnamese": "Xin ch\u00e0o, r\u1ea5t vui \u0111\u01b0\u1ee3c g\u1eb7p b\u1ea1n.", "transliteration": "Sin chow, ret vooi duoc gap ban."},
        {"english": "Thank you very much.", "vietnamese": "C\u1ea3m \u01a1n b\u1ea1n r\u1ea5t nhi\u1ec1u.", "transliteration": "Cam on ban ret nhieu."},
        {"english": "Good morning, have a great day.", "vietnamese": "Ch\u00e0o bu\u1ed5i s\u00e1ng, ch\u00fac b\u1ea1n m\u1ed9t ng\u00e0y t\u1ed1t l\u00e0nh.", "transliteration": "Chow buoi sang, chuc ban mot ngay tot lanh."},
        {"english": "I love learning new languages.", "vietnamese": "T\u00f4i y\u00eau th\u00edch vi\u1ec7c h\u1ecdc nh\u1eefng ng\u00f4n ng\u1eef m\u1edbi.", "transliteration": "Toi yeu thich viec hoc nhung ngon ngu moi."},
        {"english": "Never give up on your dreams.", "vietnamese": "\u0110\u1eebng bao gi\u1edd t\u1eeb b\u1ecf \u01b0\u1edbc m\u01a1 c\u1ee7a b\u1ea1n.", "transliteration": "Dung bao gio tu bo uoc mo cua ban."},
        {"english": "Every day is a fresh start.", "vietnamese": "M\u1ed7i ng\u00e0y l\u00e0 m\u1ed9t s\u1ef1 kh\u1edfi \u0111\u1ea7u m\u1edbi.", "transliteration": "Moi ngay la mot su khoi dau moi."},
        {"english": "Believe in yourself always.", "vietnamese": "Lu\u00f4n tin t\u01b0\u1edfng v\u00e0o b\u1ea3n th\u00e2n.", "transliteration": "Luen tin tuong vao ban than."},
        {"english": "Small steps lead to big changes.", "vietnamese": "Nh\u1eefng b\u01b0\u1edbc \u0111i nh\u1ecf d\u1eabn \u0111\u1ebfn nh\u1eefng thay \u0111\u1ed5i l\u1edbn.", "transliteration": "Nhung buoc di nho dan den nhung thay doi lon."},
        {"english": "You are stronger than you think.", "vietnamese": "B\u1ea1n m\u1ea1nh m\u1ebd h\u01a1n b\u1ea1n ngh\u0129.", "transliteration": "Ban manh me hon ban nghi."},
        {"english": "Happiness is a choice, choose it.", "vietnamese": "H\u1ea1nh ph\u00fac l\u00e0 m\u1ed9t s\u1ef1 l\u1ef1a ch\u1ecdn, h\u00e3y ch\u1ecdn n\u00f3.", "transliteration": "Hanh phuc la mot su lua chon, hay chon no."},
        {"english": "What time is it please.", "vietnamese": "Xin h\u1ecfi m\u1ea5y gi\u1edd r\u1ed3i \u1ea1?", "transliteration": "Sin hoi may gio roi a?"},
        {"english": "Where is the train station.", "vietnamese": "Nh\u00e0 ga t\u00e0u h\u1ecfa \u1edf \u0111\u00e2u?", "transliteration": "Nha ga tau hoa o dau?"},
        {"english": "How much does this cost.", "vietnamese": "C\u00e1i n\u00e0y gi\u00e1 bao nhi\u00eau?", "transliteration": "Cai nay gia bao nhieu?"},
        {"english": "Can you help me please.", "vietnamese": "B\u1ea1n c\u00f3 th\u1ec3 gi\u00fap t\u00f4i \u0111\u01b0\u1ee3c kh\u00f4ng?", "transliteration": "Ban co the giup toi duoc khong?"},
        {"english": "I would like a coffee please.", "vietnamese": "T\u00f4i mu\u1ed1n m\u1ed9t ly c\u00e0 ph\u00ea.", "transliteration": "Toi muon mot ly ca phe."},
        {"english": "The food is delicious today.", "vietnamese": "\u0110\u1ed3 \u0103n h\u00f4m nay ngon qu\u00e1.", "transliteration": "Do an hom nay ngon qua."},
        {"english": "Have a wonderful weekend.", "vietnamese": "Ch\u00fac b\u1ea1n cu\u1ed1i tu\u1ea7n vui v\u1ebb.", "transliteration": "Chuc ban cuoi tuan vui ve."},
        {"english": "Take care of yourself.", "vietnamese": "H\u00e3y t\u1ef1 ch\u0103m s\u00f3c b\u1ea3n th\u00e2n.", "transliteration": "Hay tu cham soc ban than."},
        {"english": "See you tomorrow my friend.", "vietnamese": "H\u1eb9n g\u1eb7p b\u1ea1n ng\u00e0y mai nh\u00e9.", "transliteration": "Hen gap ban ngay mai nhe."},
        {"english": "The weather is beautiful outside.", "vietnamese": "Th\u1eddi ti\u1ebft b\u00ean ngo\u00e0i th\u1eadt \u0111\u1eb9p.", "transliteration": "Thoi tiet ben ngoai that dep."},
        {"english": "I am very happy today.", "vietnamese": "T\u00f4i r\u1ea5t vui h\u00f4m nay.", "transliteration": "Toi ret vui hom nay."},
        {"english": "Learning a language opens new doors.", "vietnamese": "H\u1ecdc m\u1ed9t ng\u00f4n ng\u1eef m\u1edf ra nh\u1eefng c\u00e1nh c\u1eeda m\u1edbi.", "transliteration": "Hoc mot ngon ngu mo ra nhung canh cua moi."},
        {"english": "Keep practicing every single day.", "vietnamese": "H\u00e3y ti\u1ebfp t\u1ee5c luy\u1ec7n t\u1eadp m\u1ed7i ng\u00e0y.", "transliteration": "Hay tiep tuc luyen tap moi ngay."},
        {"english": "You can achieve anything you want.", "vietnamese": "B\u1ea1n c\u00f3 th\u1ec3 \u0111\u1ea1t \u0111\u01b0\u1ee3c b\u1ea5t c\u1ee9 \u0111i\u1ec1u g\u00ec b\u1ea1n mu\u1ed1n.", "transliteration": "Ban co the dat duoc bat cu dieu gi ban muon."},
        {"english": "Rest when you are tired.", "vietnamese": "H\u00e3y ngh\u1ec9 ng\u01a1i khi b\u1ea1n m\u1ec7t m\u1ecfi.", "transliteration": "Hay nghi ngoi khi ban met moi."},
        {"english": "Focus on the positive things.", "vietnamese": "H\u00e3y t\u1eadp trung v\u00e0o nh\u1eefng \u0111i\u1ec1u t\u00edch c\u1ef1c.", "transliteration": "Hay tap trung vao nhung dieu tich cuc."},
        {"english": "Learn from your mistakes.", "vietnamese": "H\u00e3y h\u1ecdc h\u1ecfi t\u1eeb nh\u1eefng sai l\u1ea7m c\u1ee7a b\u1ea1n.", "transliteration": "Hay hoc hoi tu nhung sai lam cua ban."},
        {"english": "Trust the process completely.", "vietnamese": "H\u00e3y tin t\u01b0\u1edfng ho\u00e0n to\u00e0n v\u00e0o qu\u00e1 tr\u00ecnh.", "transliteration": "Hay tin tuong hoan toan vao qua trinh."},
        {"english": "Breathe deeply and stay calm.", "vietnamese": "H\u00edt th\u1edf s\u00e2u v\u00e0 gi\u1eef b\u00ecnh t\u0129nh.", "transliteration": "Hit tho sau va giu binh tinh."},
        {"english": "Enjoy the little moments in life.", "vietnamese": "H\u00e3y t\u1eadn h\u01b0\u1edfng nh\u1eefng kho\u1ea3nh kh\u1eafc nh\u1ecf b\u00e9 trong cu\u1ed9c s\u1ed1ng.", "transliteration": "Hay tan huong nhung khoanh khac nho be trong cuoc song."},
        {"english": "Smile more, worry less.", "vietnamese": "H\u00e3y c\u01b0\u1eddi nhi\u1ec1u h\u01a1n, b\u1edbt lo l\u1eafng.", "transliteration": "Hay cuoi nhieu hon, bot lo lang."},
        {"english": "Be kind to everyone you meet.", "vietnamese": "H\u00e3y t\u1eed t\u1ebf v\u1edbi t\u1ea5t c\u1ea3 m\u1ecdi ng\u01b0\u1eddi b\u1ea1n g\u1eb7p.", "transliteration": "Hay tu te voi tat ca moi nguoi ban gap."},
        {"english": "Help others without expecting anything back.", "vietnamese": "Gi\u00fap \u0111\u1ee1 ng\u01b0\u1eddi kh\u00e1c m\u00e0 kh\u00f4ng mong \u0111\u1ee3i nh\u1eadn l\u1ea1i \u0111i\u1ec1u g\u00ec.", "transliteration": "Giup do nguoi khac ma khong mong doi nhan lai dieu gi."},
        {"english": "Forgive yourself and move forward.", "vietnamese": "H\u00e3y tha th\u1ee9 cho b\u1ea3n th\u00e2n v\u00e0 ti\u1ebfn v\u1ec1 ph\u00eda tr\u01b0\u1edbc.", "transliteration": "Hay tha thu cho ban than va tien ve phia truoc."},
        {"english": "Stay strong in difficult times.", "vietnamese": "H\u00e3y m\u1ea1nh m\u1ebd trong nh\u1eefng l\u00fac kh\u00f3 kh\u0103n.", "transliteration": "Hay manh me trong nhung luc kho khan."},
        {"english": "Every moment is a new beginning.", "vietnamese": "M\u1ed7i kho\u1ea3nh kh\u1eafc l\u00e0 m\u1ed9t s\u1ef1 kh\u1edfi \u0111\u1ea7u m\u1edbi.", "transliteration": "Moi khoanh khac la mot su khoi dau moi."},
        {"english": "Listen to your heart always.", "vietnamese": "Lu\u00f4n l\u1eafng nghe tr\u00e1i tim b\u1ea1n.", "transliteration": "Luen lang nghe trai tim ban."},
        {"english": "Do what makes you happy.", "vietnamese": "H\u00e3y l\u00e0m nh\u1eefng g\u00ec khi\u1ebfn b\u1ea1n h\u1ea1nh ph\u00fac.", "transliteration": "Hay lam nhung gi khien ban hanh phuc."},
        {"english": "Your potential is unlimited.", "vietnamese": "Ti\u1ec1m n\u0103ng c\u1ee7a b\u1ea1n l\u00e0 v\u00f4 h\u1ea1n.", "transliteration": "Tiem nang cua ban la vo han."},
        {"english": "Be brave and take risks.", "vietnamese": "H\u00e3y d\u0169ng c\u1ea3m v\u00e0 ch\u1ea5p nh\u1eadn r\u1ee7i ro.", "transliteration": "Hay dung cam va chap nhan rui ro."},
        {"english": "Celebrate your progress every day.", "vietnamese": "H\u00e3y \u0103n m\u1eebng s\u1ef1 ti\u1ebfn b\u1ed9 c\u1ee7a b\u1ea1n m\u1ed7i ng\u00e0y.", "transliteration": "Hay an mung su tien bo cua ban moi ngay."},
        {"english": "Surround yourself with good people.", "vietnamese": "H\u00e3y bao quanh m\u00ecnh v\u1edbi nh\u1eefng ng\u01b0\u1eddi t\u1ed1t.", "transliteration": "Hay bao quanh minh voi nhung nguoi tot."},
        {"english": "Read books and grow your mind.", "vietnamese": "\u0110\u1ecdc s\u00e1ch v\u00e0 ph\u00e1t tri\u1ec3n tr\u00ed tu\u1ec7 c\u1ee7a b\u1ea1n.", "transliteration": "Doc sach va phat trien tri tue cua ban."},
        {"english": "Travel and discover new places.", "vietnamese": "Du l\u1ecbch v\u00e0 kh\u00e1m ph\u00e1 nh\u1eefng \u0111\u1ecba \u0111i\u1ec3m m\u1edbi.", "transliteration": "Du lich va kham pha nhung dia diem moi."},
        {"english": "Appreciate what you already have.", "vietnamese": "H\u00e3y tr\u00e2n tr\u1ecdng nh\u1eefng g\u00ec b\u1ea1n \u0111\u00e3 c\u00f3.", "transliteration": "Hay tran trong nhung gi ban da co."},
        {"english": "Dance like nobody is watching.", "vietnamese": "H\u00e3y nh\u1ea3y m\u00faa nh\u01b0 th\u1ec3 kh\u00f4ng ai \u0111ang xem.", "transliteration": "Hay nhay mua nhu the khong ai dang xem."},
        {"english": "Sing from your heart out loud.", "vietnamese": "H\u00e3y h\u00e1t t\u1eeb tr\u00e1i tim b\u1ea1n th\u1eadt to.", "transliteration": "Hay hat tu trai tim ban that to."},
        {"english": "Plant seeds of kindness everywhere.", "vietnamese": "Gieo nh\u1eefng h\u1ea1t gi\u1ed1ng t\u1eed t\u1ebf \u1edf kh\u1eafp m\u1ecdi n\u01a1i.", "transliteration": "Gieo nhung hat giong tu te o khap moi noi."},
        {"english": "Let go of what you cannot control.", "vietnamese": "H\u00e3y bu\u00f4ng b\u1ecf nh\u1eefng g\u00ec b\u1ea1n kh\u00f4ng th\u1ec3 ki\u1ec3m so\u00e1t.", "transliteration": "Hay buong bo nhung gi ban khong the kiem soat."},
        {"english": "Be present in the here and now.", "vietnamese": "H\u00e3y hi\u1ec7n di\u1ec7n trong kho\u1ea3nh kh\u1eafc hi\u1ec7n t\u1ea1i.", "transliteration": "Hay hien dien trong khoanh khac hien tai."}
    ]
    fresh = [p for p in generic_fallbacks if not is_phrase_used(p["english"])]
    return fresh[:num_phrases]
async def generate_single_audio(text: str, voice: str, output_path: str):
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


async def generate_audio_with_retries(text: str, voice: str, output_path: str, max_retries: int = 3):
    import asyncio
    for attempt in range(1, max_retries + 1):
        success = await generate_single_audio(text, voice, output_path)
        if success:
            if Path(output_path).exists() and Path(output_path).stat().st_size > 100:
                return True
            else:
                print(f"    TTS file too small or missing, retrying ({attempt}/{max_retries})...")
                await asyncio.sleep(2 * attempt)
                continue
        else:
            if attempt < max_retries:
                wait = 2 * attempt
                print(f"    TTS retry {attempt}/{max_retries} in {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"    TTS failed after {max_retries} attempts, using silence fallback")
                return False
    return False


def generate_all_audio(phrases: list, output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, phrase in enumerate(phrases):
        english_file = output_dir / f"english_{i}.mp3"
        native_file = output_dir / f"native_{i}.mp3"
        combined_file = output_dir / f"combined_{i}.mp3"

        print(f"\n  Phrase {i+1}:")
        print(f"    EN: {phrase['english']}")
        print(f"    VI: {phrase['vietnamese']}")

        nat_success = asyncio.run(generate_audio_with_retries(phrase["vietnamese"], NATIVE_VOICE, str(native_file)))
        if nat_success:
            print(f"    - Vietnamese: {native_file.name}")
        else:
            print(f"    - Vietnamese: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(native_file)]
            subprocess.run(cmd, capture_output=True)

        en_success = asyncio.run(generate_audio_with_retries(phrase["english"], ENGLISH_VOICE, str(english_file)))
        if en_success:
            print(f"    - English: {english_file.name}")
        else:
            print(f"    - English: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(english_file)]
            subprocess.run(cmd, capture_output=True)

        en_duration = get_audio_duration(str(english_file))
        nat_duration = get_audio_duration(str(native_file))
        pause_between = 0.5
        total_duration = en_duration + pause_between + nat_duration

        print(f"    Total: {total_duration:.2f}s (EN: {en_duration:.2f}s + pause: {pause_between}s + VI: {nat_duration:.2f}s)")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(native_file),
            "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            concat_file = output_dir / f"concat_{i}.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                f.write(f"file '{english_file.as_posix()}'\n")
                f.write(f"file '{native_file.as_posix()}'\n")
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:a", "aac",
                str(combined_file)
            ]
            subprocess.run(cmd, capture_output=True)
            if concat_file.exists():
                concat_file.unlink()

        actual_duration = get_audio_duration(str(combined_file))
        print(f"    Combined verified: {actual_duration:.2f}s")

        audio_files.append({
            "index": i,
            "english": str(english_file),
            "native": str(native_file),
            "combined": str(combined_file),
            "duration": actual_duration,
            "en_duration": en_duration,
            "nat_duration": nat_duration
        })

    print(f"\n[audio] Generated {len(audio_files)} phrase audios")
    return audio_files


def get_audio_duration(audio_file: str) -> float:
    if not Path(audio_file).exists():
        return 2.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0


def create_final_narration(audio_files: list, output_file: str):
    n = len(audio_files)
    print(f"[audio] Combining {n} audio files...")
    concat_file = Path(output_file).parent / "narration_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for audio_info in audio_files:
            combined_path = Path(audio_info["combined"])
            if combined_path.exists():
                path_str = str(combined_path.resolve()).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "copy", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if concat_file.exists():
        concat_file.unlink()
    if result.returncode == 0 and Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        size = Path(output_file).stat().st_size
        print(f"\n[audio] Final narration: {Path(output_file).name} ({size/1024:.1f} KB)")
        return True
    return False


NOTO_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans%5Bwdth,wght%5D.ttf"
FONTS_DIR = BASE_DIR / "fonts"


def ensure_font():
    font_file = FONTS_DIR / "NotoSansVietnamese-Bold.ttf"
    if font_file.exists():
        return str(font_file)
    FONTS_DIR.mkdir(exist_ok=True)
    try:
        import urllib.request
        print(f"[font] Downloading {font_file.name}...")
        urllib.request.urlretrieve(NOTO_FONT_URL, str(font_file))
        print(f"[font] Downloaded: {font_file}")
        return str(font_file)
    except Exception as e:
        print(f"[font] Download failed: {e}")
    return None


def create_impressive_background(category_english: str):
    from PIL import Image, ImageDraw

    category_colors = {
    "Greetings": [
        [
            70,
            130,
            180
        ],
        [
            255,
            140,
            0
        ],
        [
            255,
            255,
            0
        ],
        [
            255,
            99,
            71
        ]
    ],
    "Basic Phrases": [
        [
            60,
            179,
            113
        ],
        [
            255,
            215,
            0
        ],
        [
            144,
            238,
            144
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Common Expressions": [
        [
            138,
            43,
            226
        ],
        [
            255,
            20,
            147
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            105,
            180
        ]
    ],
    "Travel": [
        [
            0,
            191,
            255
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Restaurant": [
        [
            255,
            69,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            220,
            20,
            60
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Shopping": [
        [
            255,
            105,
            180
        ],
        [
            0,
            100,
            80
        ],
        [
            255,
            192,
            203
        ],
        [
            0,
            200,
            160
        ]
    ],
    "Emergency": [
        [
            255,
            0,
            0
        ],
        [
            139,
            0,
            0
        ],
        [
            255,
            69,
            0
        ],
        [
            220,
            20,
            60
        ]
    ],
    "Family Terms": [
        [
            255,
            182,
            193
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            160,
            122
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Numbers": [
        [
            255,
            215,
            0
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            140,
            0
        ],
        [
            70,
            130,
            180
        ]
    ],
    "Time": [
        [
            0,
            0,
            100
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Motivation": [
        [
            138,
            43,
            226
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            20,
            147
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Love": [
        [
            255,
            0,
            100
        ],
        [
            139,
            0,
            0
        ],
        [
            255,
            105,
            180
        ],
        [
            255,
            192,
            203
        ]
    ],
    "Success": [
        [
            255,
            215,
            0
        ],
        [
            0,
            100,
            0
        ],
        [
            255,
            140,
            0
        ],
        [
            34,
            139,
            34
        ]
    ],
    "Wisdom": [
        [
            0,
            0,
            139
        ],
        [
            255,
            215,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            255,
            0
        ]
    ],
    "Happiness": [
        [
            255,
            255,
            0
        ],
        [
            255,
            0,
            255
        ],
        [
            255,
            165,
            0
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Self Improvement": [
        [
            0,
            128,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            0,
            255,
            0
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Gratitude": [
        [
            255,
            127,
            80
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            160,
            122
        ],
        [
            138,
            43,
            226
        ]
    ],
    "Friendship": [
        [
            255,
            192,
            203
        ],
        [
            0,
            100,
            80
        ],
        [
            255,
            105,
            180
        ],
        [
            0,
            200,
            160
        ]
    ],
    "Hope": [
        [
            0,
            0,
            100
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Creativity": [
        [
            255,
            0,
            127
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            20,
            147
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Inner Peace": [
        [
            135,
            206,
            235
        ],
        [
            0,
            0,
            100
        ],
        [
            176,
            224,
            230
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Confidence": [
        [
            255,
            69,
            0
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            140,
            0
        ],
        [
            70,
            130,
            180
        ]
    ],
    "Perseverance": [
        [
            139,
            69,
            19
        ],
        [
            255,
            215,
            0
        ],
        [
            160,
            82,
            45
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Inspiration": [
        [
            255,
            0,
            255
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            20,
            147
        ],
        [
            0,
            0,
            139
        ]
    ],
    "Positive Life": [
        [
            50,
            205,
            50
        ],
        [
            255,
            0,
            127
        ],
        [
            144,
            238,
            144
        ],
        [
            255,
            20,
            147
        ]
    ],
    "Courage": [
        [
            178,
            34,
            34
        ],
        [
            255,
            215,
            0
        ],
        [
            220,
            20,
            60
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Kindness": [
        [
            255,
            182,
            193
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            160,
            122
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Patience": [
        [
            34,
            139,
            34
        ],
        [
            255,
            255,
            0
        ],
        [
            60,
            179,
            113
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Forgiveness": [
        [
            230,
            230,
            250
        ],
        [
            75,
            0,
            130
        ],
        [
            216,
            191,
            216
        ],
        [
            138,
            43,
            226
        ]
    ],
    "Strength": [
        [
            100,
            100,
            100
        ],
        [
            255,
            69,
            0
        ],
        [
            150,
            150,
            150
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Joy": [
        [
            255,
            255,
            0
        ],
        [
            255,
            0,
            127
        ],
        [
            255,
            215,
            0
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Balance": [
        [
            60,
            179,
            113
        ],
        [
            138,
            43,
            226
        ],
        [
            152,
            251,
            152
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Growth": [
        [
            0,
            100,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            34,
            139,
            34
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Purpose": [
        [
            75,
            0,
            130
        ],
        [
            255,
            215,
            0
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Mindfulness": [
        [
            210,
            180,
            140
        ],
        [
            75,
            0,
            130
        ],
        [
            245,
            245,
            220
        ],
        [
            138,
            43,
            226
        ]
    ]
}

    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    colors = category_colors.get(category_english, [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)])

    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.33:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * (ratio * 3))
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * (ratio * 3))
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * (ratio * 3))
        elif ratio < 0.66:
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ((ratio - 0.33) * 3))
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ((ratio - 0.33) * 3))
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ((ratio - 0.33) * 3))
        else:
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * ((ratio - 0.66) * 3))
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * ((ratio - 0.66) * 3))
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * ((ratio - 0.66) * 3))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))

    for i in range(0, VIDEO_WIDTH, 120):
        for j in range(0, VIDEO_HEIGHT, 120):
            draw.ellipse(
                [(i + 30, j + 30), (i + 90, j + 90)],
                outline=(255, 255, 255, 20),
                width=1
            )

    glow = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for radius in range(800, 0, -50):
        alpha = int(30 * (1 - radius / 800))
        glow_draw.ellipse(
            [(VIDEO_WIDTH//2 - radius, VIDEO_HEIGHT//3 - radius),
             (VIDEO_WIDTH//2 + radius, VIDEO_HEIGHT//3 + radius)],
            fill=(255, 255, 255, alpha)
        )

    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glow)
    return img


def find_font(bold=False, size=40):
    from PIL import ImageFont
    if bold:
        font_preferences = [
            "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_preferences = [
            "segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for font_name in font_preferences:
        try:
            return ImageFont.truetype(font_name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = bbox
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    draw.pieslice([x1, y1, x1 + r*2, y1 + r*2], 180, 270, fill=fill)
    draw.pieslice([x2 - r*2, y1, x2, y1 + r*2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - r*2, x1 + r*2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - r*2, y2 - r*2, x2, y2], 0, 90, fill=fill)
    draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
    draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)


def generate_complete_image(phrase_data: dict, category_english: str, output_path: str, phrase_index: int = 0, total_phrases: int = 5):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL not available. Install: pip install Pillow")
        return None

    ensure_font()
    img = create_impressive_background(category_english)
    draw = ImageDraw.Draw(img)

    SIZE_CATEGORY = 64
    SIZE_NATIVE_L = 100
    SIZE_NATIVE_M = 82
    SIZE_NATIVE_S = 66
    SIZE_ENGLISH = 70
    SIZE_TRANSLITERATION = 48
    SIZE_BRANDING = 50
    SIZE_PROGRESS = 38

    font_category = find_font(bold=True, size=SIZE_CATEGORY)
    font_native_l = find_font(bold=True, size=SIZE_NATIVE_L)
    font_native_m = find_font(bold=True, size=SIZE_NATIVE_M)
    font_native_s = find_font(bold=True, size=SIZE_NATIVE_S)
    font_english = find_font(bold=True, size=SIZE_ENGLISH)
    font_transliteration = find_font(bold=False, size=SIZE_TRANSLITERATION)
    font_branding = find_font(bold=True, size=SIZE_BRANDING)
    font_progress = find_font(bold=False, size=SIZE_PROGRESS)

    native = phrase_data.get("vietnamese", "")
    english = phrase_data.get("english", "")
    transliteration = phrase_data.get("transliteration", "")

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def pick_native_font(text, max_w):
        for font, name in [(font_native_l, 'L'), (font_native_m, 'M'), (font_native_s, 'S')]:
            lines = wrap_text(text, font, max_w)
            if len(lines) <= 2:
                return font, lines
        return font_native_s, wrap_text(native, font_native_s, max_w)

    def measure_line_h(font):
        b = draw.textbbox((0, 0), "Ag", font=font)
        return b[3] - b[1]

    max_text_w = VIDEO_WIDTH - 180
    cat_native = CATEGORIES_NATIVE.get(category_english, category_english)

    nat_font, nat_lines = pick_native_font(native, max_text_w - 40)
    en_lines = wrap_text(english, font_english, max_text_w)
    trans_lines = wrap_text(transliteration, font_transliteration, max_text_w - 60) if transliteration else []

    nat_lh = measure_line_h(nat_font)
    en_lh = measure_line_h(font_english)
    trans_lh = measure_line_h(font_transliteration)

    nat_box_pad = 35
    en_box_pad = 28
    trans_box_pad = 22

    nat_box_h = len(nat_lines) * nat_lh + nat_box_pad * 2
    en_box_h = len(en_lines) * en_lh + en_box_pad * 2
    trans_box_h = len(trans_lines) * trans_lh + trans_box_pad * 2 if trans_lines else 0

    gap_cat_nat = 50
    gap_nat_en = 35
    gap_en_trans = 30
    gap_trans_prog = 25
    gap_prog_brand = 40
    prog_bar_h = 30

    total_center_h = (0 + gap_cat_nat + nat_box_h + gap_nat_en +
                      en_box_h + gap_en_trans + trans_box_h + gap_trans_prog +
                      prog_bar_h + gap_prog_brand)

    start_y = int((VIDEO_HEIGHT - total_center_h) * 0.38)
    if start_y < 200:
        start_y = 200

    cy = start_y

    # Category bar (rounded)
    cat_text = category_english
    cat_bb = draw.textbbox((0, 0), cat_text, font=font_category)
    cat_tw = cat_bb[2] - cat_bb[0]
    cat_th = cat_bb[3] - cat_bb[1]
    cat_cx = VIDEO_WIDTH // 2
    cat_cy = 185
    cat_pad = 28
    cat_box_x1 = cat_cx - cat_tw // 2 - cat_pad
    cat_box_y1 = cat_cy - cat_th // 2 - cat_pad
    cat_box_x2 = cat_cx + cat_tw // 2 + cat_pad
    cat_box_y2 = cat_cy + cat_th // 2 + cat_pad
    rounded_rect(draw, (cat_box_x1, cat_box_y1, cat_box_x2, cat_box_y2),
                 25, fill=(0, 0, 0, 190))
    draw.text((cat_cx, cat_cy), cat_text,
              fill=(255, 255, 255), font=font_category, anchor="mm",
              stroke_width=2, stroke_fill=(0, 0, 0))

    cy += gap_cat_nat

    # English phrase (top)
    en_margin = 50
    rounded_rect(draw, (en_margin, cy, VIDEO_WIDTH - en_margin, cy + en_box_h), 28,
                 fill=(20, 40, 100, 220))
    for i, line in enumerate(en_lines):
        ly = cy + en_box_pad + i * en_lh + en_lh // 2
        draw.text((VIDEO_WIDTH // 2, ly), line,
                  fill=(255, 255, 255), font=font_english, anchor="mm",
                  stroke_width=3, stroke_fill=(0, 0, 40))

    cy += en_box_h + gap_nat_en

    # Vietnamese phrase (below English)
    nat_margin = 70
    rounded_rect(draw, (nat_margin, cy, VIDEO_WIDTH - nat_margin, cy + nat_box_h), 24,
                 fill=(139, 0, 0, 220))
    for i, line in enumerate(nat_lines):
        ly = cy + nat_box_pad + i * nat_lh + nat_lh // 2
        draw.text((VIDEO_WIDTH // 2, ly), line,
                  fill=(255, 255, 200), font=nat_font, anchor="mm",
                  stroke_width=2, stroke_fill=(60, 0, 0))

    cy += nat_box_h + gap_en_trans

    # Transliteration
    if trans_lines:
        trans_margin = 90
        rounded_rect(draw, (trans_margin, cy, VIDEO_WIDTH - trans_margin, cy + trans_box_h), 18,
                     fill=(40, 40, 40, 220))
        for i, line in enumerate(trans_lines):
            ly = cy + trans_box_pad + i * trans_lh + trans_lh // 2
            draw.text((VIDEO_WIDTH // 2, ly), line,
                      fill=(220, 220, 220), font=font_transliteration, anchor="mm",
                      stroke_width=1, stroke_fill=(20, 20, 20))
        cy += trans_box_h + gap_trans_prog
    else:
        cy += gap_trans_prog

    # Progress
    prog_text = f"{phrase_index + 1} / {total_phrases}"
    prog_bb = draw.textbbox((0, 0), prog_text, font=font_progress)
    prog_h = prog_bb[3] - prog_bb[1]
    draw.text((VIDEO_WIDTH // 2, cy + prog_h // 2), prog_text,
              fill=(180, 180, 180), font=font_progress, anchor="mm")

    # Branding (rounded)
    brand_text = "VELOCITY VIETNAMESE"
    brand_bb = draw.textbbox((0, 0), brand_text, font=font_branding)
    brand_tw = brand_bb[2] - brand_bb[0]
    brand_th = brand_bb[3] - brand_bb[1]
    brand_cx = VIDEO_WIDTH // 2
    brand_cy = VIDEO_HEIGHT - 120
    brand_pad = 32
    brand_box_x1 = brand_cx - brand_tw // 2 - brand_pad
    brand_box_y1 = brand_cy - brand_th // 2 - brand_pad
    brand_box_x2 = brand_cx + brand_tw // 2 + brand_pad
    brand_box_y2 = brand_cy + brand_th // 2 + brand_pad
    rounded_rect(draw, (brand_box_x1, brand_box_y1, brand_box_x2, brand_box_y2),
                 30, fill=(0, 0, 0, 195))
    draw.text((brand_cx, brand_cy), brand_text,
              fill=(255, 215, 0), font=font_branding, anchor="mm",
              stroke_width=2, stroke_fill=(0, 0, 0))

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    print(f"  Image: {Path(output_path).name}")
    return output_path


def create_video_from_images_audio(image_files: list, audio_files: list, combined_audio: str, output_file: str):
    print(f"\n[video] Creating video from {len(image_files)} images...")
    print(f"[video] Ensuring complete audio playback and sync...")

    temp_clips = []

    for i, (img_path, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']
        print(f"  Image {i+1}/{len(image_files)}: {duration:.2f}s (EN: {audio_info.get('en_duration', 0):.1f}s + VI: {audio_info.get('nat_duration', 0):.1f}s)")

        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    concat_file = Path(output_file).parent / "concat_list.txt"

    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(temp_video)]
    subprocess.run(cmd, check=True, capture_output=True)

    print("[video] Adding audio (ensuring complete playback)...")
    audio_duration = get_audio_duration(combined_audio)
    print(f"[video] Audio duration: {audio_duration:.2f}s")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(combined_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    video_duration = get_audio_duration(str(output_file).replace(".mp4", ".mp4"))
    print(f"[video] Video created: {Path(output_file).name} ({video_duration:.2f}s)")

    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()


def generate_reel(category_english: str = None):
    if not category_english:
        category_english = get_available_category()

    print(f"\n{'='*80}")
    print(f"Category: {category_english} ({CATEGORIES_NATIVE[category_english]})")
    print(f"{'='*80}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reel_dir = VIDEO_DIR / f"{category_english}_{timestamp}"
    reel_dir.mkdir(exist_ok=True)

    print("[1/4] Generating unique phrases (checking history)...")
    phrases = generate_phrases(category_english, num_phrases=5)

    for i, phrase in enumerate(phrases, 1):
        print(f"  {i}. {phrase['english']} -> {phrase['vietnamese']}")

    print("\n[2/4] Generating images with impressive backgrounds...")
    for i, phrase in enumerate(phrases):
        output_path = reel_dir / f"phrase_{i:02d}.jpg"
        generate_complete_image(phrase, category_english, str(output_path), phrase_index=i, total_phrases=len(phrases))
        print(f"  Image {i+1}: {phrase['english'][:40]}...")

    print("\n[3/4] Generating audio (English + Vietnamese with 500ms pause)...")
    audio_files = generate_all_audio(phrases, str(reel_dir))

    final_audio = reel_dir / "narration.mp3"
    create_final_narration(audio_files, str(final_audio))

    print("\n[4/4] Creating video...")
    output_video = reel_dir / "final_reel.mp4"

    image_files = sorted([str(p) for p in reel_dir.glob("phrase_*.jpg")])

    create_video_from_images_audio(
        image_files,
        audio_files,
        str(final_audio),
        str(output_video)
    )

    metadata = {
        "category_english": category_english,
        "category_native": CATEGORIES_NATIVE[category_english],
        "timestamp": timestamp,
        "phrases": phrases,
        "video": str(output_video),
        "audio": str(final_audio)
    }

    with open(reel_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"REEL COMPLETE!")
    print(f"  {reel_dir}")
    print(f"  {output_video.name}")
    print(f"  Branding: VELOCITY VIETNAMESE")
    print(f"{'='*80}\n")

    return metadata


if __name__ == "__main__":
    print("\n" + "="*80)
    print(f"VELOCITY VIETNAMESE - FACEBOOK REELS AUTOMATION")
    print("="*80)
    print("\nFEATURES:")
    print("  - Natural pauses with commas (non-robotic TTS)")
    print("  - Perfect audio-video synchronization")
    print("  - Complete audio playback guaranteed")
    print("  - English category names (for learners)")
    print(f"  - VELOCITY VIETNAMESE branding at bottom")
    print("  - NEVER repeats phrases (permanent history tracking)")
    print(f"\nAVAILABLE CATEGORIES ({len(CATEGORIES_ENGLISH)} total):")
    for i, cat in enumerate(CATEGORIES_ENGLISH, 1):
        print(f"   {i:2d}. {cat} ({CATEGORIES_NATIVE[cat]})")
    print("="*80)

    generate_reel()

    print("\n" + "="*80)
    print("READY FOR DAILY AUTOMATION!")
    print("="*80)
