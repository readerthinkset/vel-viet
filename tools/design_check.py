"""Render scene stills from a synthetic timeline (no TTS / no network)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from engine.timeline import build_timeline
from engine.renderer import capture_stills

PHRASES = [
    {"english": "Where is the train station?", "vietnamese": "Nhà ga tàu hỏa ở đâu?",
     "transliteration": "Nha ga tau hoa o dau?"},
    {"english": "Could you recommend a good restaurant nearby?", "vietnamese": "Bạn có thể giới thiệu một nhà hàng ngon gần đây không?",
     "transliteration": "Ban co the gioi thieu mot nha hang ngon gan day khong?"},
    {"english": "How much does this cost?", "vietnamese": "Cái này giá bao nhiêu tiền?",
     "transliteration": "Cai nay gia bao nhieu tien?"},
    {"english": "Can you help me, please?", "vietnamese": "Bạn có thể giúp tôi được không?",
     "transliteration": "Ban co the giup toi duoc khong?"},
    {"english": "Have a wonderful weekend!", "vietnamese": "Chúc bạn cuối tuần vui vẻ!",
     "transliteration": "Chuc ban cuoi tuan vui ve!"},
]


def fake_clip(index, phrase):
    en_words = phrase["english"].split()
    vi_words = phrase["vietnamese"].split()
    en_dur = 0.42 * len(en_words) + 0.45
    vi_dur = 0.5 * len(vi_words) + 0.55
    return {
        "index": index,
        "en_duration": en_dur,
        "vi_duration": vi_dur,
        "en_words": [{"start": i * 0.42 + 0.05, "end": i * 0.42 + 0.36} for i in range(len(en_words))],
        "vi_words": [{"start": i * 0.5 + 0.06, "end": i * 0.5 + 0.44} for i in range(len(vi_words))],
    }


def main():
    clips = [fake_clip(i, p) for i, p in enumerate(PHRASES)]
    tl = build_timeline(PHRASES, clips, "Travel")
    p0, p1 = tl["phrases"][0], tl["phrases"][1]
    times = [
        1.55,
        3.20,
        p0["en_end"] - 0.25,
        p0["nat_reveal"] + 0.95,
        p0["vi_end"] + 0.32,
        p0["vi_repeat_start"] + 0.55,
        p1["nat_reveal"] + 0.95,
        p1["vi_repeat_start"] + 0.9,
        tl["outro"]["start"] + 0.9,
        tl["outro"]["start"] + 3.4,
    ]
    print(f"duration: {tl['duration']:.2f}s")
    for t in times:
        print(f"  still at {t:.2f}s")
    saved = capture_stills(tl, times, ROOT / "output" / "design_test")
    for p in saved:
        print(p)


if __name__ == "__main__":
    main()
