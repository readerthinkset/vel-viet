"""AI phrase generation with permanent no-repeat history."""

from __future__ import annotations

import json
import random
from datetime import datetime

import requests

import config
from config import CATEGORIES, CATEGORIES_NATIVE, CATEGORY_META, HISTORY_DIR, MAX_RECENT_CATEGORIES

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"

FALLBACK_PHRASES = [
    {"english": "Hello, nice to meet you.", "vietnamese": "Xin chào, rất vui được gặp bạn.", "transliteration": "Sin chow, ret vooi duoc gap ban."},
    {"english": "Thank you very much.", "vietnamese": "Cảm ơn bạn rất nhiều.", "transliteration": "Cam on ban ret nhieu."},
    {"english": "Good morning, have a great day.", "vietnamese": "Chào buổi sáng, chúc bạn một ngày tốt lành.", "transliteration": "Chow buoi sang, chuc ban mot ngay tot lanh."},
    {"english": "I love learning new languages.", "vietnamese": "Tôi yêu thích việc học những ngôn ngữ mới.", "transliteration": "Toi yeu thich viec hoc nhung ngon ngu moi."},
    {"english": "Never give up on your dreams.", "vietnamese": "Đừng bao giờ từ bỏ ước mơ của bạn.", "transliteration": "Dung bao gio tu bo uoc mo cua ban."},
    {"english": "Every day is a fresh start.", "vietnamese": "Mỗi ngày là một sự khởi đầu mới.", "transliteration": "Moi ngay la mot su khoi dau moi."},
    {"english": "Believe in yourself always.", "vietnamese": "Luôn tin tưởng vào bản thân.", "transliteration": "Luen tin tuong vao ban than."},
    {"english": "Small steps lead to big changes.", "vietnamese": "Những bước đi nhỏ dẫn đến những thay đổi lớn.", "transliteration": "Nhung buoc di nho dan den nhung thay doi lon."},
    {"english": "You are stronger than you think.", "vietnamese": "Bạn mạnh mẽ hơn bạn nghĩ.", "transliteration": "Ban manh me hon ban nghi."},
    {"english": "Happiness is a choice, choose it.", "vietnamese": "Hạnh phúc là một sự lựa chọn, hãy chọn nó.", "transliteration": "Hanh phuc la mot su lua chon, hay chon no."},
    {"english": "What time is it please.", "vietnamese": "Xin hỏi mấy giờ rồi ạ?", "transliteration": "Sin hoi may gio roi a?"},
    {"english": "Where is the train station.", "vietnamese": "Nhà ga tàu hỏa ở đâu?", "transliteration": "Nha ga tau hoa o dau?"},
    {"english": "How much does this cost.", "vietnamese": "Cái này giá bao nhiêu?", "transliteration": "Cai nay gia bao nhieu?"},
    {"english": "Can you help me please.", "vietnamese": "Bạn có thể giúp tôi được không?", "transliteration": "Ban co the giup toi duoc khong?"},
    {"english": "I would like a coffee please.", "vietnamese": "Tôi muốn một ly cà phê.", "transliteration": "Toi muon mot ly ca phe."},
    {"english": "The food is delicious today.", "vietnamese": "Đồ ăn hôm nay ngon quá.", "transliteration": "Do an hom nay ngon qua."},
    {"english": "Have a wonderful weekend.", "vietnamese": "Chúc bạn cuối tuần vui vẻ.", "transliteration": "Chuc ban cuoi tuan vui ve."},
    {"english": "Take care of yourself.", "vietnamese": "Hãy tự chăm sóc bản thân.", "transliteration": "Hay tu cham soc ban than."},
    {"english": "See you tomorrow my friend.", "vietnamese": "Hẹn gặp bạn ngày mai nhé.", "transliteration": "Hen gap ban ngay mai nhe."},
    {"english": "The weather is beautiful outside.", "vietnamese": "Thời tiết bên ngoài thật đẹp.", "transliteration": "Thoi tiet ben ngoai that dep."},
    {"english": "I am very happy today.", "vietnamese": "Tôi rất vui hôm nay.", "transliteration": "Toi ret vui hom nay."},
    {"english": "Learning a language opens new doors.", "vietnamese": "Học một ngôn ngữ mở ra những cánh cửa mới.", "transliteration": "Hoc mot ngon ngu mo ra nhung canh cua moi."},
    {"english": "Keep practicing every single day.", "vietnamese": "Hãy tiếp tục luyện tập mỗi ngày.", "transliteration": "Hay tiep tuc luyen tap moi ngay."},
    {"english": "You can achieve anything you want.", "vietnamese": "Bạn có thể đạt được bất cứ điều gì bạn muốn.", "transliteration": "Ban co the dat duoc bat cu dieu gi ban muon."},
    {"english": "Rest when you are tired.", "vietnamese": "Hãy nghỉ ngơi khi bạn mệt mỏi.", "transliteration": "Hay nghi ngoi khi ban met moi."},
    {"english": "Focus on the positive things.", "vietnamese": "Hãy tập trung vào những điều tích cực.", "transliteration": "Hay tap trung vao nhung dieu tich cuc."},
    {"english": "Learn from your mistakes.", "vietnamese": "Hãy học hỏi từ những sai lầm của bạn.", "transliteration": "Hay hoc hoi tu nhung sai lam cua ban."},
    {"english": "Trust the process completely.", "vietnamese": "Hãy tin tưởng hoàn toàn vào quá trình.", "transliteration": "Hay tin tuong hoan toan vao qua trinh."},
    {"english": "Breathe deeply and stay calm.", "vietnamese": "Hít thở sâu và giữ bình tĩnh.", "transliteration": "Hit tho sau va giu binh tinh."},
    {"english": "Enjoy the little moments in life.", "vietnamese": "Hãy tận hưởng những khoảnh khắc nhỏ bé trong cuộc sống.", "transliteration": "Hay tan huong nhung khoanh khac nho be trong cuoc song."},
    {"english": "Smile more, worry less.", "vietnamese": "Hãy cười nhiều hơn, bớt lo lắng.", "transliteration": "Hay cuoi nhieu hon, bot lo lang."},
    {"english": "Be kind to everyone you meet.", "vietnamese": "Hãy tử tế với tất cả mọi người bạn gặp.", "transliteration": "Hay tu te voi tat ca moi nguoi ban gap."},
    {"english": "Help others without expecting anything back.", "vietnamese": "Giúp đỡ người khác mà không mong đợi nhận lại điều gì.", "transliteration": "Giup do nguoi khac ma khong mong doi nhan lai dieu gi."},
    {"english": "Forgive yourself and move forward.", "vietnamese": "Hãy tha thứ cho bản thân và tiến về phía trước.", "transliteration": "Hay tha thu cho ban than va tien ve phia truoc."},
    {"english": "Stay strong in difficult times.", "vietnamese": "Hãy mạnh mẽ trong những lúc khó khăn.", "transliteration": "Hay manh me trong nhung luc kho khan."},
    {"english": "Every moment is a new beginning.", "vietnamese": "Mỗi khoảnh khắc là một sự khởi đầu mới.", "transliteration": "Moi khoanh khac la mot su khoi dau moi."},
    {"english": "Listen to your heart always.", "vietnamese": "Luôn lắng nghe trái tim bạn.", "transliteration": "Luen lang nghe trai tim ban."},
    {"english": "Do what makes you happy.", "vietnamese": "Hãy làm những gì khiến bạn hạnh phúc.", "transliteration": "Hay lam nhung gi khien ban hanh phuc."},
    {"english": "Your potential is unlimited.", "vietnamese": "Tiềm năng của bạn là vô hạn.", "transliteration": "Tiem nang cua ban la vo han."},
    {"english": "Be brave and take risks.", "vietnamese": "Hãy dũng cảm và chấp nhận rủi ro.", "transliteration": "Hay dung cam va chap nhan rui ro."},
    {"english": "Celebrate your progress every day.", "vietnamese": "Hãy ăn mừng sự tiến bộ của bạn mỗi ngày.", "transliteration": "Hay an mung su tien bo cua ban moi ngay."},
    {"english": "Surround yourself with good people.", "vietnamese": "Hãy bao quanh mình với những người tốt.", "transliteration": "Hay bao quanh minh voi nhung nguoi tot."},
    {"english": "Read books and grow your mind.", "vietnamese": "Đọc sách và phát triển trí tuệ của bạn.", "transliteration": "Doc sach va phat trien tri tue cua ban."},
    {"english": "Travel and discover new places.", "vietnamese": "Du lịch và khám phá những địa điểm mới.", "transliteration": "Du lich va kham pha nhung dia diem moi."},
    {"english": "Appreciate what you already have.", "vietnamese": "Hãy trân trọng những gì bạn đã có.", "transliteration": "Hay tran trong nhung gi ban da co."},
    {"english": "Dance like nobody is watching.", "vietnamese": "Hãy nhảy múa như thể không ai đang xem.", "transliteration": "Hay nhay mua nhu the khong ai dang xem."},
    {"english": "Sing from your heart out loud.", "vietnamese": "Hãy hát từ trái tim bạn thật to.", "transliteration": "Hay hat tu trai tim ban that to."},
    {"english": "Plant seeds of kindness everywhere.", "vietnamese": "Gieo những hạt giống tử tế ở khắp mọi nơi.", "transliteration": "Gieo nhung hat giong tu te o khap moi noi."},
    {"english": "Let go of what you cannot control.", "vietnamese": "Hãy buông bỏ những gì bạn không thể kiểm soát.", "transliteration": "Hay buong bo nhung gi ban khong the kiem soat."},
    {"english": "Be present in the here and now.", "vietnamese": "Hãy hiện diện trong khoảnh khắc hiện tại.", "transliteration": "Hay hien dien trong khoanh khac hien tai."},
]


def _load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_phrase_history():
    data = _load_json(PHRASE_HISTORY_FILE, {"phrases": [], "last_updated": None})
    data.setdefault("phrases", [])
    return data


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    _save_json(PHRASE_HISTORY_FILE, data)


def is_phrase_used(english):
    english_lower = english.lower().strip()
    for p in load_phrase_history()["phrases"]:
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            "vietnamese": phrase["vietnamese"],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat(),
        })
    save_phrase_history(history)
    print(f"[content] Saved {len(phrases)} phrases (history total: {len(history['phrases'])})")


def get_available_category():
    data = _load_json(RECENT_CATEGORIES_FILE, {"recent_categories": [], "last_updated": None})
    recent = data.get("recent_categories", [])
    available = [c for c in CATEGORIES if c not in recent]
    if not available:
        recent = recent[-5:]
        available = [c for c in CATEGORIES if c not in recent]
        print("[rotation] Reset recent categories")
    selected = random.choice(available)
    recent.append(selected)
    data["recent_categories"] = recent[-MAX_RECENT_CATEGORIES:]
    data["last_updated"] = datetime.now().isoformat()
    _save_json(RECENT_CATEGORIES_FILE, data)
    print(f"[rotation] Category: {selected} ({len(available)} available)")
    return selected


def _normalize_phrase(item):
    if not isinstance(item, dict):
        return None
    english = str(item.get("english", "")).strip()
    native = str(item.get("vietnamese") or item.get("vietnamese_text") or item.get("native") or "").strip()
    translit = str(item.get("transliteration") or item.get("romaji") or "").strip()
    if not english or not native:
        return None
    if len(english.split()) > 16 or len(native.split()) > 16:
        return None
    if "/" in native or "|" in native:
        native = native.split("/")[0].split("|")[0].strip()
    if not translit:
        translit = ""
    return {
        "english": english.replace("  ", " ").strip(),
        "vietnamese": native.strip(),
        "transliteration": translit.strip().strip("[]"),
    }


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE[category_english]
    history = load_phrase_history()
    recent_english = [
        p["english"] for p in history["phrases"] if p.get("category") == category_english
    ][-30:]

    if config.POLLINATIONS_API_KEY:
        for attempt in range(3):
            try:
                phrases = _request_phrases(category_english, category_native, recent_english, num_phrases, attempt)
                unique = []
                for item in phrases:
                    p = _normalize_phrase(item)
                    if not p:
                        continue
                    if is_phrase_used(p["english"]):
                        continue
                    if any(p["english"].lower() == u["english"].lower() for u in unique):
                        continue
                    unique.append(p)
                    if len(unique) >= num_phrases:
                        break
                if len(unique) >= num_phrases:
                    add_phrases_to_history(unique[:num_phrases], category_english)
                    return unique[:num_phrases]
                print(f"[content] Attempt {attempt + 1}: only {len(unique)} fresh phrases (need {num_phrases})")
            except Exception as exc:  # noqa: BLE001 - network boundary
                print(f"[content] Attempt {attempt + 1} failed: {exc}")
    else:
        print("[content] No POLLINATIONS_API_KEY, using fallback phrases")

    fresh_fallback = [p for p in FALLBACK_PHRASES if not is_phrase_used(p["english"])]
    chosen = fresh_fallback[:num_phrases]
    if len(chosen) < num_phrases:
        chosen = FALLBACK_PHRASES[:num_phrases]
    add_phrases_to_history(chosen, category_english)
    return chosen


def _request_phrases(category_english, category_native, recent_english, num_phrases, attempt):
    avoid = ""
    if recent_english:
        avoid = "\nDo NOT reuse any of these phrases:\n" + "\n".join(f"- {p}" for p in recent_english)

    prompt = f"""Create {num_phrases * 6} unique {category_english} phrases for English speakers learning Vietnamese.
{avoid}

Rules:
1. Keep every phrase short and natural (4-11 words per language).
2. Use natural commas for TTS breathing pauses.
3. Each phrase must be speakable in 2-4 seconds.
4. Write clean Vietnamese with full diacritics. One translation only, no slashes.
5. Transliteration is a friendly Roman-script pronunciation guide (not IPA).
6. Vary the sentence patterns and emotions. No duplicates.
7. Phrases must feel like real everyday language, not textbook filler.

Return ONLY a JSON array:
[{{"english": "...", "vietnamese": "...", "transliteration": "..."}}]"""

    response = requests.post(
        "https://gen.pollinations.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.POLLINATIONS_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.AI_MODEL,
            "messages": [
                {"role": "system", "content": "You are a Vietnamese teacher creating short, natural, varied bilingual phrases. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": min(0.95 + attempt * 0.02, 1.0),
        },
        timeout=90,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()

    if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0].strip()

    start = content.find("[")
    end = content.rfind("]")
    if start >= 0 and end > start:
        content = content[start:end + 1]

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("AI did not return a JSON array")
    return data
