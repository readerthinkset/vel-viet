# Velocity Vietnamese

Automated Vietnamese-learning shorts. Every run writes a fresh AI lesson, voices it in English and Vietnamese, animates a Duolingo-style lesson in the browser, adds original music and sound design, renders a 1080x1920 MP4, and publishes it to every connected platform.

Each phrase plays three times so viewers can actually learn it: **English** → **Vietnamese** → **Vietnamese again** under a "REPEAT AFTER ME" prompt, with karaoke tiles and word clocks synced to every pass.

- Karaoke word highlighting synced to real TTS word boundaries
- Word-tile layout that auto-fits and balances long Vietnamese phrases
- Mascot "Velo", streak/XP HUD, progress bar, confetti and an outro summary card
- Procedural background music and SFX (no licensed audio)
- Permanent phrase history, so no phrase is ever repeated
- Facebook, Instagram, YouTube, VK, Telegram, Twitter/X, Threads, TikTok

## Quick start

```bash
pip install -r requirements.txt
python -m playwright install chromium
ffmpeg -version          # must be on PATH

cp .env.example .env     # add POLLINATIONS_API_KEY and any platform keys
python build.py                       # random category, 5 phrases
python build.py --category Travel --phrases 3
python build.py --open                # build, then open the interactive preview
```

Output lands in `output/lessons/<Category>_<timestamp>/`:

```
final_reel.mp4   # 1080x1920, H.264 + AAC, ~30-50s
thumbnail.jpg    # frame from the second phrase
timeline.json    # every scene/word/SFX time
mix.wav          # narration + music + SFX
metadata.json    # phrases, category, hashtags
```

Prefer a browser preview? Open `scene/preview.html` after a build and press Play. The timeline and audio are injected at build time.

## Publishing

```bash
python upload_all_platforms.py                 # newest lesson -> all connected platforms
python upload_all_platforms.py --dry-run       # show which platforms are configured
python upload_all_platforms.py --print-captions
python upload_all_platforms.py --lesson output/lessons/<Category>_<timestamp>
```

Platforms with missing credentials are skipped, never fatal. Results are written to `output/upload_results_*.json`.

## GitHub Actions

`.github/workflows/daily_5x_upload.yml` builds and publishes five times a day:

| Run (UTC) | US Eastern |
|-----------|------------|
| 12:00 | 7:00 AM |
| 14:00 | 9:00 AM |
| 17:00 | 12:00 PM |
| 20:00 | 3:00 PM |
| 00:00 | 7:00 PM |

Add these repository secrets (Settings > Secrets and variables > Actions):

| Secret | Purpose |
|--------|---------|
| `POLLINATIONS_API_KEY` | AI phrase generation |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | YouTube |
| `FACEBOOK_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID` | Facebook Reels |
| `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID` | Instagram Reels |
| `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID` | Threads |
| `TIKTOK_ACCESS_TOKEN` | TikTok |
| `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` | Twitter/X |
| `VK_ACCESS_TOKEN`, `VK_GROUP_ID` | VK |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID` | Telegram |

You can also trigger a run manually from the Actions tab.

## How a lesson is built

1. `engine/content.py` picks a category that has not run recently, asks Pollinations for fresh phrases, filters anything already in `output/history/all_generated_phrases.json`, and retries if the model repeats itself.
2. `engine/tts.py` synthesizes each English and Vietnamese line with Edge TTS and captures `WordBoundary` events. Each line is validated for real audio (peak level, not just duration) and retried with a secondary voice if needed. If boundaries are missing, karaoke timing falls back to a character-weighted estimate.
3. `engine/timeline.py` lays out intro, phrase scenes and outro, then derives absolute word clocks, the Vietnamese repeat pass (`vi_repeat_start`/`vi_repeat_end`), SFX cues and confetti bursts.
4. `engine/audio.py` synthesizes the music bed and SFX with numpy, places the English line, the first Vietnamese pass and the repeat pass, ducks the music under speech, and writes a 48 kHz stereo mix.
5. `engine/renderer.py` loads `scene/index.html` in headless Chromium, injects the timeline, calls `window.seek(t)` for every frame at 30 fps, and pipes JPEG frames into FFmpeg.
6. `upload_all_platforms.py` builds per-platform captions (YouTube metadata, 280-char X post, Threads variant) and uploads.

Everything is deterministic: a timeline plus the same fonts always renders the same video.

## Customization

- `config.py` - brand, voices, speech rates, timings, 55 categories with Vietnamese names, icons and accent colors, hashtags.
- `scene/scene.css` - layout and look. Card offsets, tile styling, HUD, intro and outro.
- `scene/scene.js` - animation logic. `seek(t)` drives every property, so motion is frame-accurate.
- `scene/icons.js` - icon set and the Velo mascot SVG.
- `engine/audio.py` - music progression, tempo, SFX recipes.
- `tools/design_check.py` - renders scene stills from a synthetic timeline in a few seconds, useful when tuning visuals without waiting for a full video.

Phrase history lives in `output/history/`. It is committed back to the repo by the workflow; never delete it unless you want phrases to repeat.

## Project structure

```
velocity vietnamese/
  build.py                     # end-to-end lesson builder
  config.py                    # language pack + design constants
  upload_all_platforms.py      # caption builder and publisher
  engine/
    content.py                 # AI phrases, history, category rotation
    tts.py                     # Edge TTS + word boundary mapping
    timeline.py                # scene timing, karaoke clocks, FX cues
    audio.py                   # music, SFX, mixdown
    renderer.py                # Chromium capture -> FFmpeg -> MP4
  scene/
    index.html, scene.css, scene.js, icons.js
    fonts/                     # bundled Nunito + Noto Sans
  upload/                      # one module per platform
  output/
    lessons/                   # rendered lessons
    history/                   # permanent phrase history
  tools/design_check.py
  .github/workflows/daily_5x_upload.yml
```

## Notes and troubleshooting

- Rendering speed is roughly 1.5-4 fps depending on the machine; a 5-phrase lesson takes several minutes. GitHub Actions is configured with a 75-minute timeout.
- `playwright install chromium` is required once per machine. On Linux CI use `--with-deps`.
- Edge TTS throttles when too many websockets open at once, so synthesis runs with low concurrency and per-phrase sequencing. Each line gets four attempts (with silent-output detection), then the configured fallback voice; if both voices fail the build stops instead of shipping a silent video.
- Vietnamese diacritics are rendered with the bundled Noto Sans variable font, so no system font packages are needed.
- The intro uses a vertical logo lockup (`VELOCITY` + `VIETNAMESE`). To adapt this engine to another language, change `config.py` and the text in `scene/index.html`.
