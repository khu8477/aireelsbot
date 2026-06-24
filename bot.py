import os
import asyncio
import requests
import edge_tts
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_KEY"))

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
    try:
        requests.post(url, data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": msg})
    except:
        pass

def clean_server():
    """تنظيف الملفات المؤقتة بعد الانتهاء"""
    for f in os.listdir("."):
        if f.endswith((".jpg", ".mp4", ".png", ".mp3")):
            try:
                os.remove(f)
            except:
                pass

async def generate_voice(text):
    """توليد تعليق صوتي"""
    communicate = edge_tts.Communicate(text, "ar-SA-ZariNeural")
    await communicate.save("story_audio.mp3")

def run_pipeline():
    try:
        send_telegram("🚀 البوت بدأ العمل - جاري إنتاج القصة...")
        
        # 1. إنشاء السكربت
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        prompt = "اكتب قصة فواكه درامية من 5 مشاهد. لكل مشهد اكتب وصفاً دقيقاً (Prompt) بالإنجليزية بستايل سينمائي."
        script = model.generate_content(prompt).text
        
        # 2. توليد الصوت
        asyncio.run(generate_voice(script))
        
        # 3. توليد الصور والتحريك (باستيراد الأدوات التي برمجناها)
        from fal_engine import generate_image
        from pixverse_engine import animate_image
        
        images = [generate_image(f"Scene {i}") for i in range(5)]
        scenes = [animate_image(img) for img in images]
        
        # 4. المونتاج
        clips = [VideoFileClip(s).set_duration(8) for s in scenes]
        final = concatenate_videoclips(clips, method="compose")
        final = final.set_audio(AudioFileClip("story_audio.mp3"))
        final.write_videofile("final_story.mp4", fps=24, codec="libx264", audio_codec="aac")
        
        # 5. النشر على فيسبوك
        url = f"https://graph.facebook.com/{os.getenv('FB_PAGE_ID')}/videos"
        files = {"file": open("final_story.mp4", 'rb')}
        data = {"access_token": os.getenv("FB_TOKEN"), "description": "قصة فواكه سينمائية جديدة! 🍎✨"}
        
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            send_telegram("✅ تم النشر بنجاح على فيسبوك!")
        else:
            send_telegram(f"⚠️ فشل النشر: {response.text}")
            
    except Exception as e:
        send_telegram(f"❌ حدث خطأ: {str(e)}")
    finally:
        clean_server()

if __name__ == "__main__":
    run_pipeline()
                
