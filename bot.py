import os
import asyncio
import requests
import edge_tts
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from fal_engine import generate_image
from pixverse_engine import animate_image

genai.configure(api_key=os.getenv("GEMINI_KEY"))

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
    requests.post(url, data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": msg})

def clean_server():
    for f in os.listdir("."):
        if f.endswith((".jpg", ".mp4", ".png", ".mp3")):
            os.remove(f)

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, "ar-SA-ZariNeural")
    await communicate.save("story_audio.mp3")

def run_pipeline():
    try:
        send_telegram("🚀 البوت بدأ العمل - إنتاج القصة السينمائية...")
        
        # 1. السكربت
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        prompt = "اكتب قصة فواكه من 5 مشاهد (40 ثانية). لكل مشهد اعطني Prompt سينمائي بالإنجليزية (3D render, Pixar-style, cinematic lighting)."
        script = model.generate_content(prompt).text
        
        # 2. توليد الصوت والصور والتحريك
        asyncio.run(generate_voice(script))
        images = [generate_image(f"Scene {i}") for i in range(5)]
        scenes = [animate_image(img) for img in images]
        
        # 3. المونتاج
        clips = [VideoFileClip(s).set_duration(8) for s in scenes]
        final = concatenate_videoclips(clips, method="compose")
        final = final.set_audio(AudioFileClip("story_audio.mp3"))
        final.write_videofile("final_story.mp4", fps=24, codec="libx264", audio_codec="aac")
        
        # 4. النشر
        url = f"https://graph.facebook.com/{os.getenv('FB_PAGE_ID')}/videos"
        files = {"file": open("final_story.mp4", 'rb')}
        data = {"access_token": os.getenv("FB_TOKEN"), "description": "قصة اليوم 🍎✨"}
        requests.post(url, data=data, files=files)
        
        send_telegram("✅ تم النشر بنجاح!")
    except Exception as e:
        send_telegram(f"❌ خطأ: {str(e)}")
    finally:
        clean_server()

if __name__ == "__main__":
    run_pipeline()
    
