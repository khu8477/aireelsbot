import google.generativeai as genai
import requests, json, os, shutil
from moviepy.editor import *
from gTTS import gTTS
import time
from datetime import datetime

# ===== المفاتيح من GitHub Secrets =====
GEMINI_KEY = os.getenv("GEMINI_KEY")
HAILUO_KEY = os.getenv("HAILUO_KEY")
FB_TOKEN = os.getenv("FB_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
TELEGRAM_TOKEN = os.getenv("8762140567:AAGsSz7yqa0Y79w4R7kmT8ZiB65Ia3pP-tc")
TELEGRAM_CHAT_ID = os.getenv("8669512229")

TEMP = "temp"
os.makedirs(TEMP, exist_ok=True)

def send_tg(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
        except: pass

def hunt_trend_and_create_story():
    send_tg("🎬 كنقلب على الترند دابا...")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro', tools="google_search_retrieval")
    prompt = f"""Today is {datetime.now().strftime('%Y-%m-%d %H:%M')}.
    Search Facebook Reels + TikTok trending topics RIGHT NOW in Arabic world.
    Find viral emotional story with high engagement.
    Create 5 scenes, 6 seconds each, vertical 9:16 format.
    Character must be 3D Pixar style fruit or vegetable.
    Each dialogue max 8 words, emotional, dramatic.
    Return JSON array only: [{{"character":"","image_prompt":"","motion_prompt":"","dialogue":""}}]"""
    res = model.generate_content(prompt)
    text = res.text.replace("```json","").replace("```","").strip()
    return json.loads(text)

def generate_hailuo_video(prompt, motion, num):
    headers = {"Authorization": f"Bearer {HAILUO_KEY}", "Content-Type": "application/json"}
    data = {"prompt": f"{prompt}. {motion}. 3D Pixar style, cinematic lighting, ultra detailed, 1080x1920", "duration": 6, "aspect_ratio": "9:16", "motion_strength": 5}
    r = requests.post("https://api.hailuoai.com/v1/video/generations", headers=headers, json=data, timeout=180)
    if r.status_code!= 200: raise Exception(f"Hailuo error: {r.text}")
    task_id = r.json()["id"]
    send_tg(f"🎬 Scene {num+1}/5: كنتسنى Hailuo...")
    while True:
        status = requests.get(f"https://api.hailuoai.com/v1/video/generations/{task_id}", headers=headers, timeout=60).json()
        if status["status"] == "succeeded":
            video_url = status["output"]["url"]
            break
        elif status["status"] == "failed": raise Exception("Hailuo failed")
        time.sleep(10)
    path = f"{TEMP}/scene_{num}.mp4"
    with open(path, 'wb') as f: f.write(requests.get(video_url, timeout=120).content)
    return path

def add_voice_and_clean(video_path, text, num):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_path = f"{TEMP}/voice_{num}.mp3"
    tts.save(audio_path)
    clip = VideoFileClip(video_path).crop(y1=65, y2=-65) # قص الشريط الأسود ديال Hailuo
    audio = AudioFileClip(audio_path)
    final = clip.set_audio(audio).fx(vfx.fadein, 0.3).fx(vfx.fadeout, 0.3)
    out_path = f"{TEMP}/final_{num}.mp4"
    final.write_videofile(out_path, fps=24, codec='libx264', audio_codec='aac', bitrate="3000k", logger=None)
    return out_path

def publish_to_facebook(video_path, desc):
    send_tg("📤 كننشر فالفيسبوك دابا...")
    with open(video_path, 'rb') as v:
        r = requests.post(f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/videos",
            files={'file': v}, data={'access_token': FB_TOKEN, 'description': desc}, timeout=300)
    if r.status_code == 200:
        send_tg(f"✅ تم النشر فقط! Video ID: {r.json().get('id')}")
        return True
    else:
        error = r.json().get('error',{}).get('message','Unknown error')
        send_tg(f"⚠️ خطأ النشر: {error}")
        return False

def main():
    video_paths = []
    try:
        scenes = hunt_trend_and_create_story()
        topic = scenes[0]['image_prompt'][:40]
        send_tg(f"🔥 الترند: {topic}\n🎭 الشخصية: {scenes[0]['character']}")

        for i, s in enumerate(scenes):
            video = generate_hailuo_video(s['image_prompt'], s['motion_prompt'], i)
            final_video = add_voice_and_clean(video, s['dialogue'], i)
            video_paths.append(final_video)
            send_tg(f"✅ Scene {i+1}/5 واجد")

        send_tg("🎞️ كنجمع المشاهد ففيديو واحد...")
        clips = [VideoFileClip(v) for v in video_paths]
        story = concatenate_videoclips(clips, method="compose")
        final_path = "story.mp4"
        story.write_videofile(final_path, fps=24, codec='libx264', bitrate="3500k", logger=None)

        genai.configure(api_key=GEMINI_KEY)
        desc_prompt = f"Write viral Facebook Reels description in Arabic + 6 trending hashtags for story about: {topic}"
        desc = genai.GenerativeModel('gemini-1.5-flash').generate_content(desc_prompt).text
        publish_to_facebook(final_path, desc)

    except Exception as e:
        send_tg(f"⚠️ خطأ عام: {str(e)[:250]}")
    finally:
        if os.path.exists(TEMP): shutil.rmtree(TEMP)
        if os.path.exists("story.mp4"): os.remove("story.mp4")
        send_tg("🗑️ تم مسح الملفات - البوت سالا")

if __name__ == "__main__":
    main()
