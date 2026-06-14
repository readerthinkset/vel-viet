"""
Upload videos to VK (VKontakte) using vk_api library
"""
import os
import vk_api
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def upload_to_vk(video_path, description="", title=""):
    access_token = os.getenv('VK_ACCESS_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')

    def mask(s): return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else ("PLACEHOLDER (***)" if s == "***" else "MISSING")
    print(f"[vk] Group ID: {group_id}")
    print(f"[vk] Access Token: {mask(access_token)}")

    if not access_token or access_token == "***":
        print("VK access token missing. Skipping.")
        return {'status': 'skipped', 'reason': 'missing_credentials'}
    if not group_id or group_id == "***":
        print("VK group ID missing. Skipping.")
        return {'status': 'skipped', 'reason': 'missing_credentials'}

    try:
        group_id_clean = str(group_id).lstrip('-')
        group_id_int = int(group_id_clean)
    except ValueError:
        print(f"Invalid Group ID: '{group_id}'. Skipping.")
        return {'status': 'skipped', 'reason': 'invalid_group_id'}

    print(f"VK upload starting...")
    print(f"Video: {video_path}")

    try:
        vk_session = vk_api.VkApi(token=access_token)
        vk = vk_session.get_api()
        upload = vk_api.VkUpload(vk_session)

        message = description if description else "Learn Vietnamese with VELOCITY VIETNAMESE!"
        if not message.strip():
            message = "New video!"

        print("Uploading video to VK...")
        video = upload.video(
            video_file=str(video_path),
            name=title or 'VELOCITY VIETNAMESE',
            description=description[:220] if description else '',
            group_id=group_id_int,
            wallpost=0
        )

        print(f"Video uploaded! ID: {video['video_id']}")

        attachment = f"video{video['owner_id']}_{video['video_id']}"
        post_result = vk.wall.post(
            owner_id=-group_id_int,
            from_group=1,
            message=message,
            attachments=attachment
        )

        post_id = post_result['post_id']
        post_url = f"https://vk.com/wall-{group_id_int}_{post_id}"
        print(f"Posted to wall! URL: {post_url}")

        return {
            'success': True,
            'video_id': video['video_id'],
            'owner_id': video['owner_id'],
            'post_id': post_id,
            'post_url': post_url,
            'message': 'Video uploaded and posted to VK successfully'
        }

    except vk_api.exceptions.ApiError as e:
        raise Exception(f"VK API Error: {e}")
    except FileNotFoundError:
        raise Exception(f"Video file not found: {video_path}")
    except Exception as e:
        raise Exception(f"Failed to upload to VK: {e}")


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python upload_vk.py <video_path> [description] [title]")
        sys.exit(1)
    video_path = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else "Learn Vietnamese with VELOCITY VIETNAMESE!"
    title = sys.argv[3] if len(sys.argv) > 3 else "VELOCITY VIETNAMESE"
    try:
        result = upload_to_vk(video_path, description, title)
        print(f"Success! {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
