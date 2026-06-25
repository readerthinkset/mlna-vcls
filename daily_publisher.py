import os
import json
import glob
import random
import requests
import shutil
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Import upload functions
try:
    from upload.upload_instagram import upload_to_instagram
    from upload.upload_threads import upload_to_threads
    from upload.upload_facebook import upload_to_facebook, upload_to_facebook_story
    from upload.upload_to_youtube import upload_to_youtube
except ImportError as e:
    print(f"Error importing upload modules: {e}")
    # Still want to proceed or stop?
    pass

PROCESSED_DIR = "Processed_Videos"
PUBLISHED_LOG = "published_videos.json"

def get_already_published():
    if os.path.exists(PUBLISHED_LOG):
        with open(PUBLISHED_LOG, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def get_repost_counts():
    """Count how many times each video has been posted."""
    published = get_already_published()
    counts = {}
    for entry in published:
        vname = entry.get("video_name", "")
        counts[vname] = counts.get(vname, 0) + 1
    return counts

def mark_as_published(video_name, metadata):
    published = get_already_published()
    published.append({
        "video_name": video_name,
        "metadata": metadata
    })
    with open(PUBLISHED_LOG, 'w', encoding='utf-8') as f:
        json.dump(published, f, indent=4)

def select_video(specific_video=None):
    published = [item["video_name"] for item in get_already_published()]
    all_videos = sorted(glob.glob(os.path.join(PROCESSED_DIR, "*.mp4")))

    if specific_video:
        # specific_video might be a full path or just a filename
        if os.path.exists(specific_video):
            # It's a full path
            vid_path = specific_video
            name = os.path.basename(specific_video)
        else:
            # It's just a filename, join with PROCESSED_DIR
            vid_path = os.path.join(PROCESSED_DIR, specific_video)
            name = specific_video

        if os.path.exists(vid_path):
            if name in published:
                post_count = sum(1 for p in published if p == name)
                print(f"🔄 Video {name} was already published ({post_count}x) - Re-publishing (recycling)")
            return vid_path, name
        else:
            print(f"❌ Error: Specific video {name} not found")
            return None, None

    # Find unpublished videos first
    unpublished = [(vid, os.path.basename(vid)) for vid in all_videos if os.path.basename(vid) not in published]

    if unpublished:
        vid, name = unpublished[0]
        return vid, name

    # All videos published - use weighted random selection (less posted = more likely)
    if all_videos:
        repost_counts = get_repost_counts()
        weights = []
        for vid in all_videos:
            name = os.path.basename(vid)
            count = repost_counts.get(name, 0)
            weight = max(1, 1000 // (3 ** min(count, 6)))
            weights.append(weight)

        selected_vid = random.choices(all_videos, weights=weights, k=1)[0]
        name = os.path.basename(selected_vid)
        post_count = repost_counts.get(name, 0)
        print(f"🎲 All videos published. Weighted random reuse (posted {post_count}x): {name}")
        return selected_vid, name

    return None, None

def generate_caption():
    import random
    import time

    api_key = os.getenv("POLLINATIONS_API_KEY")
    model = os.getenv("AI_MODEL", "openai")

    fallback_titles = [
        "Milana sings 'Someone Like You' - Adele Cover 🎤",
        "Beautiful Vocal Cover of 'Flowers' by Miley Cyrus 🌸",
        "Milana vocals - 'Lose Yourself' Emotional Cover",
        "Singing 'Let It Be' by The Beatles - Cover 🎵",
        "Milana - 'Rolling in the Deep' Powerful Cover",
        "Acoustic Cover of 'Perfect' by Ed Sheeran 🎸",
        "Milana Sings 'Hallelujah' - Haunting Vocal Performance",
        "Pop Medley 2025 - Milana Vocal Cover 🔥",
        "Singing 'Someone You Loved' - Lewis Capaldi Cover",
        "Milana vocals - 'Shallow' from A Star is Born 🎬",
        "R&B Medley - Milana Vocal Performance 🎶",
        "Acoustic Session: 'Stay With Me' by Sam Smith",
        "Milana - 'I Will Always Love You' Powerful Cover",
        "Soft Vocal Cover of 'All of Me' by John Legend",
        "Milana Sings Your Favorite Songs - Request Cover 🎵",
    ]

    fallback_descriptions = [
        "Milana's voice will give you chills 🎤✨ In this video, she performs a stunning vocal cover of 'Someone Like You' by Adele. Her emotional delivery and incredible range make this cover truly special. If you love music and beautiful voices, you've found the right page! Drop a 🔥 if you love Adele too! #milanavocals #adele #someone like you #coversong #vocals #singing #musiccover #popularsongs #singersofinstagram",
        "Milana is back with another AMAZING vocal performance! 🌸 This time she's covering 'Flowers' by Miley Cyrus with her own unique twist. Her voice brings something fresh to this hit song. Which song should she cover next? Tell us in the comments! 🎤 #milanavocals #flowers #mileycyrus #cover #singing #vocals #music #popularmusic #coversong",
        "Milana takes on 'Lose Yourself' by Eminem — but with her own melodic style! 🎵 This cover transforms one of the most iconic rap songs into a beautiful vocal performance. You've never heard it like this before. Like if this surprised you! 🔥 #milanavocals #loseyourself #eminem #cover #vocals #singing #musiccover #uniquecover #artist",
        "Let It Be by The Beatles, sung by Milana 🎹 This timeless classic gets a fresh, heartfelt treatment. Her voice carries the emotion of the song beautifully. Close your eyes and just listen... Share this with someone who loves The Beatles! 🎶 #milanavocals #letitbe #thebeatles #cover #classics #vocals #singing #music #feelings",
        "Rolling in the Deep — Milana's powerhouse vocal cover of Adele! 🔥 She brings the intensity and soul of this song to life. The high notes will give you goosebumps. Can we get a 📢 for this talent? Comment your rating 1-10! ⬇️ #milanavocals #rollinginthedeep #adele #cover #powerhouse #vocals #singing #musiccover",
        "Milana's acoustic cover of 'Perfect' by Ed Sheeran on guitar 🎸✨ There's something magical about a voice and a guitar. This stripped-down version will melt your heart. Tag someone you'd dedicate this song to! 💕 #milanavocals #perfect #edsheeran #acousticcover #guitar #vocals #romantic #music #coversong",
        "Hallelujah — one of the most beautiful songs ever written, performed by Milana 🕯️ Her emotional delivery of this Leonard Cohen classic is absolutely haunting. This is the kind of performance that stops you in your tracks. Save this to listen again later! 🎵 #milanavocals #hallelujah #leonardcohen #cover #emotional #vocals #singing #powerfulperformance",
        "Milana brings you a pop medley of 2025's biggest hits! 🔥 From trending TikTok songs to radio anthems — she sings them all in one seamless performance. How many songs can you recognize? Comment below! 🎤 #milanavocals #popmedley #2025hits #cover #medley #vocals #trending #music",
        "'Someone You Loved' by Lewis Capaldi — Milana's emotional cover 🥺 This song is already heartbreaking, but her voice adds a whole new layer of emotion. If you've ever lost someone, this one hits different. Drop a 🕊️ if this touched your heart. #milanavocals #someoneyouloved #lewiscapaldi #cover #emotional #vocals #singing",
        "Shallow — from A Star is Born 🎬 Milana performs this iconic duet as a solo vocal masterpiece. She captures every ounce of emotion from the film. Lady Gaga would be proud! Like if you want to hear more movie covers! 🎥 #milanavocals #shallow #astarisborn #cover #ladygaga #bradleycooper #vocals #moviesongs",
        "R&B Medley by Milana — smooth, soulful, and absolutely stunning 🎶 She covers the best R&B hits in one beautiful performance. Her runs and vocal control are next level. If you're an R&B fan, you NEED to follow this page! Comment your favorite R&B song! 🎤 #milanavocals #rnb #r&bmedley #cover #soul #vocals #singing #smooth",
        "Stay With Me by Sam Smith — acoustic session with Milana 🎤 This stripped-down version highlights the raw power and emotion of her voice. No fancy effects, just pure talent. Share this with someone who needs to hear something beautiful today. 🌙 #milanavocals #staywithme #samsmith #acoustic #cover #vocals #puretalent",
        "Milana sings 'I Will Always Love You' — Whitney Houston's legendary song 💎 This is one of the hardest songs to sing, and she NAILS IT. The power, the emotion, the iconic high notes... Whitney would smile. Drop a 👑 if you think this is royalty-worthy! #milanavocals #iwillalwaysloveyou #whitneyhouston #cover #legendary #vocals #powerful",
        "All of Me by John Legend — Milana's soft and romantic cover 💕 This love song gets the most tender treatment. Perfect for a quiet evening or a moment of reflection. Tag your special someone to let them know they have ALL of you! 🌹 #milanavocals #allofme #johnlegend #cover #romantic #love #vocals #acoustic",
        "Milana is taking YOUR requests! 🎤 Comment a song you want to hear her sing, and she might cover it next! In the meantime, enjoy this beautiful performance. She loves connecting with her fans through music. Which song should she sing next? Comment below! ⬇️ #milanavocals #request #cover #youchoose #vocals #singing #interactive #musiccommunity",
    ]

    if not api_key:
        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        print("Warning: POLLINATIONS_API_KEY not found. Using fallback captions.")
        return chosen_title, chosen_desc

    vibes = [
        "soulful and emotional — make listeners feel the music deeply",
        "energetic and exciting — get viewers hyped about the performance",
        "warm and intimate — create a personal connection through song",
        "passionate and powerful — showcase the full range of the voice",
        "gentle and soothing — give viewers a moment of peace and beauty",
        "uplifting and joyful — spread positive energy through music",
        "captivating and mesmerizing — leave viewers in awe of the talent",
    ]
    chosen_vibe = random.choice(vibes)

    prompt = (
        f"Write a completely unique, long, and captivating title and description for a short video "
        f"for the social media page 'Milana Vocals'. "
        f"The page features Milana singing beautiful vocal covers of popular songs across all genres — pop, rock, R&B, classics, and more. Her voice is powerful, emotional, and captivating. "
        f"It's all about the love of music and sharing incredible vocal talent with the world. "
        f"Speak as a passionate music lover who is amazed by Milana's talent and wants to share it with everyone. "
        f"Make the vibe {chosen_vibe}. "
        f"The description should be LONG (4-6 sentences minimum), engaging, and focused on the music. "
        f"Include engagement calls-to-action such as: "
        f"- Like if you love this cover! "
        f"- Comment your favorite song below! "
        f"- Share with someone who loves music! "
        f"- Follow Milana Vocals for more amazing covers! "
        f"Include relevant hashtags in ALL LOWERCASE such as #milanavocals #cover #vocals #singing #musiccover #popularsongs #coversong #acoustic #music #singersongwriter #pop #rnb #songwriter. "
        f"Return ONLY a valid JSON object in this format: {{\"title\": \"<title>\", \"description\": \"<description>\"}} "
        f"Do not include any other text or markdown block backticks."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "seed": random.randint(1, 999999)
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        return result.get("title", chosen_title), result.get("description", chosen_desc)
    except Exception as e:
        print(f"Error generating caption: {e}")
        return random.choice(fallback_titles), random.choice(fallback_descriptions)

def main():
    print("=" * 60)
    print("🚀 DAILY AUTOMATION STARTING")
    print("=" * 60)
    
    specific_video = sys.argv[1] if len(sys.argv) > 1 else None
    video_path, video_name = select_video(specific_video)
    if not video_path:
        print("✅ No new videos found to publish. Exiting.")
        return
        
    print(f"👉 Selected Video: {video_name}")
    print("🧠 Generating caption via Pollination AI...")
    title, description = generate_caption()
    
    print(f"📝 Title: {title}")
    print(f"📝 Description:\n{description}")
    
    # Combined caption for platforms that use a single text field
    combined_caption = f"{title}\n\n{description}"
    
    success_flags = {
        "instagram_reel": False,
        "instagram_story": False,
        "facebook_reel": False,
        "facebook_story": False,
        "threads": False,
        "youtube": False
    }
    
    # Instagram Reels
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=False)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Instagram Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_reel"] = True
    except Exception as e:
        print(f"❌ Instagram Reel upload failed: {e}")
        
    # Instagram Stories
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=True)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Instagram Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_story"] = True
    except Exception as e:
        print(f"❌ Instagram Story upload failed: {e}")
        
    # Facebook Reels
    try:
        result = upload_to_facebook(video_path, description, title=title)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Facebook Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_reel"] = True
    except Exception as e:
        print(f"❌ Facebook Reel upload failed: {e}")
        
    # Facebook Stories
    try:
        result = upload_to_facebook_story(video_path)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Facebook Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_story"] = True
    except Exception as e:
        print(f"❌ Facebook Story upload failed: {e}")
        
    # Threads
    try:
        result = upload_to_threads(video_path, combined_caption)
        if result and result.get('status') == 'skipped':
            print(f"⚠️  Threads: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["threads"] = True
    except Exception as e:
        print(f"❌ Threads upload failed: {e}")
        
    # YouTube Shorts
    try:
        upload_to_youtube(video_path, title, description, tags=["milanavocals", "cover", "vocals", "singing", "musiccover", "popularsongs", "coversong", "acoustic", "music", "pop", "rnb", "singersongwriter", "vocalperformance", "talent"])
        success_flags["youtube"] = True
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        
    # Record as published regardless of partial success,
    # to avoid repeating the same video. Alternatively, only record if fully successful.
    print("\n✅ Marking video as published.")
    
    # Check if this is a recycled video (already in published_videos.json)
    published_list = get_already_published()
    is_recycled = any(item["video_name"] == video_name for item in published_list)
    
    if is_recycled:
        print(f"   🔄 This is a recycled video (re-publishing)")
    
    mark_as_published(video_name, {
        "title": title,
        "description": description,
        "success_flags": success_flags,
        "recycled": is_recycled
    })
    
    # Move the published video to Published_Videos folder
    published_dir = "Published_Videos"
    if not os.path.exists(published_dir):
        os.makedirs(published_dir)
        
    try:
        dest_path = os.path.join(published_dir, video_name)
        shutil.move(video_path, dest_path)
        print(f"📦 Moved published video to {dest_path}")
    except Exception as e:
        print(f"❌ Failed to move published video: {e}")
    
    print("🎉 DAILY AUTOMATION COMPLETE")

if __name__ == "__main__":
    main()
