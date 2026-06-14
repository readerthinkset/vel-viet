"""
Instagram Reels Upload - Using tmpfiles.org for Public URL
"""

import os
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def upload_to_instagram(video_path, caption, is_story=False):
    media_type = 'STORIES' if is_story else 'REELS'

    print("\n" + "=" * 60)
    print(f"INSTAGRAM {media_type} UPLOAD STARTING")
    print("=" * 60)

    access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN') or os.getenv('FACEBOOK_ACCESS_TOKEN')
    user_id = os.getenv('INSTAGRAM_ACCOUNT_ID') or os.getenv('IG_USER_ID')

    def mask(s): return f"{s[:10]}...{s[-4:]}" if s and len(s) > 10 else ("PLACEHOLDER" if s == "***" else "MISSING")
    print(f"[instagram] User ID: {user_id}")
    print(f"[instagram] Access Token: {mask(access_token)}")

    if not access_token:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN not set")

    if access_token.startswith('IGAA'):
        print("[instagram] Detected IGAA token (Instagram Basic/Standard API)")
        print("[instagram] Fetching correct ID...")
        try:
            me_resp = requests.get(f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}", timeout=10)
            if me_resp.status_code == 200:
                me_data = me_resp.json()
                detected_id = me_data.get('id')
                if detected_id and detected_id != user_id:
                    print(f"[instagram] Using detected ID: {detected_id}")
                    user_id = detected_id
        except Exception as e:
            print(f"[instagram] ID verification error: {e}")

    if not user_id:
        raise ValueError("INSTAGRAM_ACCOUNT_ID not set")

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = video_path_obj.stat().st_size / (1024 * 1024)
    print(f"[instagram] Video: {video_path} ({file_size_mb:.2f} MB)")

    caption_limited = caption[:2200] if len(caption) > 2200 else caption
    print(f"[instagram] Caption: {len(caption_limited)} chars")

    try:
        print(f"[instagram] Step 1: Uploading to temporary hosting...")
        with open(video_path_obj, 'rb') as video_file:
            files = {'file': ('video.mp4', video_file, 'video/mp4')}
            temp_response = requests.post(
                'https://tmpfiles.org/api/v1/upload',
                files=files,
                timeout=180
            )
        if temp_response.status_code != 200:
            raise Exception(f"Temporary hosting failed: {temp_response.status_code}")

        temp_data = temp_response.json()
        if temp_data.get('status') != 'success':
            raise Exception(f"Temporary hosting failed: {temp_data}")

        temp_url = temp_data.get('data', {}).get('url', '')
        video_url = temp_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
        print(f"[instagram] Temporary URL: {video_url}")

        print(f"[instagram] Step 2: Creating Instagram {media_type} container...")
        container_url = f"https://graph.instagram.com/v21.0/{user_id}/media"
        container_params = {
            'media_type': media_type,
            'video_url': video_url,
            'access_token': access_token
        }
        if not is_story:
            container_params['caption'] = caption_limited
            container_params['share_to_feed'] = 'true'
            container_params['thumb_offset'] = '5000'

        container_response = requests.post(container_url, params=container_params, timeout=60)
        if container_response.status_code != 200:
            print(f"[instagram] Retrying with Facebook Graph API endpoint...")
            container_url = f"https://graph.facebook.com/v21.0/{user_id}/media"
            container_response = requests.post(container_url, params=container_params, timeout=60)
            if container_response.status_code != 200:
                error_data = container_response.json() if container_response.text else {}
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"Instagram Container Error: {error_msg}")

        container_id = container_response.json().get('id')
        print(f"[instagram] Container created: {container_id}")

        print(f"[instagram] Step 3: Waiting for video processing...")
        max_wait = 180
        waited = 0
        while waited < max_wait:
            status_url = f"https://graph.instagram.com/v21.0/{container_id}"
            status_params = {
                'fields': 'status_code',
                'access_token': access_token
            }
            status_response = requests.get(status_url, params=status_params, timeout=30)
            if status_response.status_code != 200:
                status_url = f"https://graph.facebook.com/v21.0/{container_id}"
                status_response = requests.get(status_url, params=status_params, timeout=30)

            status_data = status_response.json()
            status_code = status_data.get('status_code', 'UNKNOWN')
            print(f"[instagram] Status: {status_code} (waited {waited}s)")

            if status_code == 'FINISHED':
                print(f"[instagram] Video processing complete!")
                break
            elif status_code == 'ERROR':
                error_msg = status_data.get('error_message', 'Video processing failed')
                raise Exception(error_msg)
            time.sleep(10)
            waited += 10

        if waited >= max_wait:
            raise Exception("Video processing timed out")

        print(f"[instagram] Step 4: Publishing...")
        time.sleep(5)
        publish_url = f"https://graph.instagram.com/v21.0/{user_id}/media_publish"
        publish_params = {
            'creation_id': container_id,
            'access_token': access_token
        }

        max_publish_retries = 3
        publish_response = None
        for attempt in range(max_publish_retries):
            publish_response = requests.post(publish_url, params=publish_params, timeout=60)
            if publish_response.status_code == 200:
                break
            else:
                print(f"[instagram] Publish attempt {attempt+1} failed. Retrying...")
                time.sleep(10)
            if attempt == max_publish_retries - 1:
                publish_url = f"https://graph.facebook.com/v21.0/{user_id}/media_publish"
                publish_response = requests.post(publish_url, params=publish_params, timeout=60)

        if not publish_response or publish_response.status_code != 200:
            error_data = publish_response.json() if publish_response and publish_response.text else {}
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"Instagram Publish Error: {error_msg}")

        media_id = publish_response.json().get('id')
        print(f"[instagram] SUCCESS! Media ID: {media_id}")
        print("=" * 60)
        return {'id': media_id, 'platform': 'instagram', 'status': 'success'}

    except Exception as e:
        print(f"[instagram] ERROR: {e}")
        print("=" * 60)
        raise


if __name__ == '__main__':
    video_file = Path('final_video.mp4')
    if video_file.exists():
        try:
            result = upload_to_instagram(str(video_file), "Test upload")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Failed: {e}")
