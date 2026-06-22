import os, requests, json, time, shutil
from moviepy.editor import *
from gTTS import gTTS
from datetime import datetime
import google.generativeai as genai

# ===== المفاتيح من GitHub Secrets =====
GEMINI_KEY = os.getenv("AIzaSyDls5vxMDx0czmfhxVmiALLyxWkdEU4ssU")
FAL_KEY = os.getenv("ce5ec315-451a-4ad4-847e-0512a7b1516d:c4b5b24d4fca141177ac9a34ebd6b33f")
FB_TOKEN = os.getenv("EAAbJhowQ7nYBRzQgzzfdfMikQDeM5nWzhn72O8RQu2OiYENfV2KhlSSBCLOHr9Ffc9bhyqBqhhQVs8nQl98suUXlcg8unTkZBcjOh3YZAPrGwURuFlm1LFZAm9QfUL5380YDbVt4OLjZA8xRS9Q5hfA8kVOWZCUHJgImC9eWK6VGiUlVYtlaTX3ZCYqKWZBL4oQflnB")
FB_PAGE_ID = os.getenv"1174722115726830"
TELEGRAM_TOKEN = os.getenv("8762140567:AAGsSz7yqa0Y79w4R7kmT8ZiB65Ia3pP-tc")
TELEGRAM_CHAT_ID = os.getenv"8669512229"

TEMP = "temp"
os.makedirs(TEMP, exist_ok=True)

def send_tg(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
        except: pass

def create_story_7_scenes():
    send_tg("🎬 Gemini كيقلب على الترند دابا...")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash', tools="google_search_retrieval")
    prompt = f"""Today {datetime.now().strftime('%Y-%m-%d')}.
    Search Facebook Reels + TikTok trending topics RIGHT NOW in Arabic world.
    Create viral emotional story: 7 scenes, each 3 seconds. Total ~21 seconds.
    Character: same 3D Pixar style fruit or vegetable in all scenes.
    Each dialogue max 7 words, emotional, dramatic Arabic.
    Return JSON array only: [{{"scene_prompt":"","dialogue":""}}]"""
    res = model.generate_content(prompt)
    text = res.text.replace("```json","").replace("```","").strip()
    return json.loads(text)

def generate_pika_fal_video(prompt, dialogue, num):
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    data = {
        "prompt": f"{prompt}, 3D Pixar style, cinematic lighting, ultra detailed, smooth motion, vertical 9:16, 1080x1920",
        "negative_prompt": "blurry, low quality, watermark, text, logo",
        "duration": "3s",
        "aspect_ratio": "9:16",
        "motion": 3
    }

    r = requests.post("https://queue.fal.run/fal-ai/pika-2.1/text-to-video", headers=headers, json=data, timeout=120)
    if r.status_code not in [200, 201]:
        send_tg(f"⚠️ خطأ Fal Scene {num+1}: {r.text}")
        return None

    request_id = r.json()["request_id"]
    send_tg(f"🎬 Scene {num+1}/7: كنتسنى Fal.ai 3-4 دقايق...")

    for _ in range(40):
        time.sleep(10)
        status = requests.get(f"https://queue.fal.run/fal-ai/pika-2.1/requests/{request_id}/status",
                             headers=headers, timeout=60).json()
        if status.get("status") == "COMPLETED":
            result = requests.get(f"https://queue.fal.run/fal-ai/pika-2.1/requests/{request_id}",
                                 headers=headers, timeout=60).json()
            video_url = result["video"]["url"]
            break
        elif status.get("status") == "FAILED":
            return None
    else:
        return None

    video_path = f"{TEMP}/scene_{num}.mp4"
    with open(video_path, 'wb') as f:
        f.write(requests.get(video_url, timeout=120).content)

    tts = gTTS(text=dialogue, lang='ar')
    audio_path = f"{TEMP}/voice_{num}.mp3"
    tts.save(audio_path)

    clip = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    final = clip.set_audio(audio).fx(vfx.fadein, 0.2).fx(vfx.fadeout, 0.2)
    out_path = f"{TEMP}/final_{num}.mp4"
    final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', logger=None)
    return out_path

def publish_facebook(video_path, desc):
    send_tg("📤 كننشر فالفيسبوك دابا...")
    with open(video_path, 'rb') as v:
        r = requests.post(f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/videos",
            files={'file': v}, data={'access_token': FB_TOKEN, 'description': desc}, timeout=300)
    if r.status_code == 200:
        send_tg(f"✅ تم النشر فقط! Video ID: {r.json().get('id')}")
        return True
    else:
        error = r.json().get('error',{}).get('message','Unknown')
        send_tg(f"⚠️ خطأ النشر: {error}")
        return False

def main():
    video_paths = []
    try:
        scenes = create_story_7_scenes()
        topic = scenes[0]['scene_prompt'][:35]
        send_tg(f"🔥 الترند: {topic}")

        for i, s in enumerate(scenes):
            video = generate_pika_fal_video(s['scene_prompt'], s['dialogue'], i)
            if video:
                video_paths.append(video)
                send_tg(f"✅ Scene {i+1}/7 واجد")
            time.sleep(5)

        send_tg("🎞️ كندمج 7 المشاهد = فيديو 21 ثانية...")
        clips = [VideoFileClip(v) for v in video_paths]
        story = concatenate_videoclips(clips, method="compose")
        final_path = "story.mp4"
        story.write_videofile(final_path, fps=24, codec='libx264', bitrate="3000k", logger=None)

        genai.configure(api_key=GEMINI_KEY)
        desc = genai.GenerativeModel('gemini-1.5-flash').generate_content(
            f"Write viral Arabic Facebook Reels description + 6 trending hashtags for story: {topic}"
        ).text
        publish_facebook(final_path, desc)

    except Exception as e:
        send_tg(f"⚠️ خطأ عام: {str(e)[:250]}")
    finally:
        if os.path.exists(TEMP): shutil.rmtree(TEMP)
        if os.path.exists("story.mp4"): os.remove("story.mp4")
        send_tg("🗑️ تم مسح الملفات - البوت سالا")

if __name__ == "__main__":
    main()
