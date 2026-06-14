"""
YouTube Upload Script - VELOCITY VIETNAMESE
Uses refresh token from GitHub Secrets to upload videos.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime

load_dotenv()


def get_authenticated_service():
    client_id = (os.getenv('YOUTUBE_CLIENT_ID') or os.getenv('YT_CLIENT_ID', '')).strip()
    client_secret = (os.getenv('YOUTUBE_CLIENT_SECRET') or os.getenv('YT_CLIENT_SECRET', '')).strip()
    refresh_token = (os.getenv('YOUTUBE_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN', '')).strip()

    def mask(s): return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else "MISSING"
    print(f"[youtube] Client ID: {mask(client_id)}")
    print(f"[youtube] Client Secret: {mask(client_secret)}")
    print(f"[youtube] Refresh Token: {mask(refresh_token)}")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "Missing credentials! Set these environment variables:\n"
            "  - YOUTUBE_CLIENT_ID\n"
            "  - YOUTUBE_CLIENT_SECRET\n"
            "  - YOUTUBE_REFRESH_TOKEN"
        )

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

    try:
        creds.refresh(Request())
    except Exception as e:
        if "invalid_grant" in str(e).lower():
            print("\n[youtube] AUTH ERROR: Refresh token has EXPIRED or been REVOKED.")
            print("SOLUTION: Generate a NEW refresh token.")
            print("   1. Go to Google Cloud Console.")
            print("   2. Ensure OAuth Consent Screen is in 'Production' or add yourself as a test user.")
            print("   3. Run a local script to get a new refresh token.")
        raise

    return build('youtube', 'v3', credentials=creds)


def generate_video_metadata(category: str, num_phrases: int, phrases: list = None):
    title = f"Vietnamese Learning: {num_phrases} Essential {category} Phrases"

    description_lines = [
        f"Learn Vietnamese with VELOCITY VIETNAMESE!",
        f"",
        f"Category: {category}",
        f"",
        f"Master Vietnamese one phrase at a time! Today's {category} lesson:",
        f""
    ]

    if phrases:
        emojis = ["1", "2", "3", "4", "5"]
        for i, phrase in enumerate(phrases[:5], 0):
            emoji = emojis[i] if i < len(emojis) else f"{i+1}."
            description_lines.append(f"{emoji}. {phrase['english']}")
            description_lines.append(f"   {phrase.get('vietnamese', '')}")
            transliteration = phrase.get('transliteration') or ''
            description_lines.append(f"   [{transliteration}]")
            description_lines.append("")

    description_lines.extend([
        f"Tip: Repeat each phrase out loud 3 times!",
        f"Like this video if you learned something new!",
        f"Comment your favorite phrase below!",
        f"Subscribe for daily Vietnamese lessons!",
        f"",
        f"Pronunciation Guide:",
        f"   The phonetic spelling in brackets helps you say it correctly!",
        f"",
        f"#LearnVietnamese #VietnameseLessons #VietnameseForBeginners #LanguageLearning",
        f"#Vietnamese #Education #Tutorial #DailyVietnamese #{category.replace(' ', '')}",
        f"#VELOCITYVIETNAMESE #VietnamesePhrases #SpeakVietnamese"
    ])

    description = "\n".join(description_lines)

    tags = [
        "learn vietnamese",
        "vietnamese lessons",
        "vietnamese for beginners",
        "vietnamese phrases",
        "language learning",
        "vietnamese tutorial",
        "speak vietnamese",
        category.lower(),
        "education",
        "daily vietnamese",
        "velocity vietnamese",
        "vietnamese learning"
    ]

    return title, description, tags


def upload_to_youtube(video_path, title, description, tags=None, category_id='22'):
    if tags is None:
        tags = ['education', 'language learning', 'vietnamese']
    youtube = get_authenticated_service()

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }

    if '#Shorts' not in body['snippet']['description']:
        body['snippet']['description'] += '\n\n#Shorts'

    media = MediaFileUpload(
        str(video_path),
        chunksize=-1,
        resumable=True,
        mimetype='video/mp4'
    )

    print(f"[youtube] Uploading: {title}")
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube] Progress: {int(status.progress() * 100)}%")

    print(f"[youtube] Uploaded! Video ID: {response['id']}")
    print(f"[youtube] URL: https://youtube.com/shorts/{response['id']}")

    return response


def main():
    video_file = Path('final_video.mp4')
    if not video_file.exists():
        print("[youtube] No video found at final_video.mp4")
        return

    title = "Learn Vietnamese Daily"
    description = "#shorts #learnvietnamese #vietnamese #language #education"
    tags = ['vietnamese', 'education', 'language learning']

    try:
        upload_to_youtube(
            video_path=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id='22'
        )
    except Exception as e:
        print(f"[youtube] Upload failed: {e}")
        raise


if __name__ == '__main__':
    main()
