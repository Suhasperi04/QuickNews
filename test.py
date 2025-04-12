"""Instagram cleanup utility"""
from utils.instagram_auth import get_client, USERNAME
import time

def delete_all_except_first(max_retries=3, retry_delay=5):
    """Delete all posts except the first one
    
    Args:
        max_retries (int): Maximum number of retries for failed operations
        retry_delay (int): Delay in seconds between retries
    """
    cl = get_client()
    user_id = cl.user_id_from_username(USERNAME)
    medias = cl.user_medias(user_id, amount=50)

    print(f"📸 Total posts found: {len(medias)}")

    for i, media in enumerate(medias):
        if i == 0:
            print(f"✅ Keeping first post: {media.pk}")
            continue
            
        retries = 0
        while retries < max_retries:
            try:
                cl.media_delete(media.pk)
                print(f"🗑️ Deleted post {i+1}: {media.pk}")
                break
            except Exception as e:
                retries += 1
                if retries == max_retries:
                    print(f"❌ Failed to delete post {i+1} after {max_retries} attempts: {e}")
                else:
                    print(f"⚠️ Error deleting post {i+1} (attempt {retries}/{max_retries}): {e}")
                    time.sleep(retry_delay)

if __name__ == "__main__":
    delete_all_except_first()
