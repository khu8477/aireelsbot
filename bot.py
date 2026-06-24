import os
import asyncio
import requests
import google.generativeai as genai

# --- حماية الاستيراد (للتعامل مع أي نسخة من moviepy) ---
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.audio.io.AudioFileClip import AudioFileClip

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_KEY"))

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
    try:
        requests.post(url, data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": msg})
    except:
        pass

def run_pipeline():
    try:
        send_telegram("🚀 البوت بدأ العمل - جاري إنتاج القصة...")
        
        # 1. إنشاء السكربت بواسطة Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        script = model.generate_content("اكتب قصة فواكه قصيرة من 3 مشاهد، اكتب وصفاً لكل مشهد بالإنجليزية.").text
        
        # 2. استيراد المحركات (تأكد من وجود fal_engine.py و pixverse_engine.py في نفس المجلد)
        from fal_engine import generate_image
        from pixverse_engine import animate_image
        
        # 3. معالجة الصور والفيديو
        images = [generate_image(f"Scene {i}") for i in range(3)]
        scenes = [animate_image(img) for img in images]
        
        # 4. المونتاج (نستخدم 5 ثوانٍ لكل مشهد)
        clips = [VideoFileClip(s).set_duration(5) for s in scenes]
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile("final_story.mp4", fps=24, codec="libx264")
        
        send_telegram("✅ تم إنتاج الفيديو بنجاح وجاهز للنشر!")
            
    except Exception as e:
        send_telegram(f"❌ حدث خطأ برمجي: {str(e)}")

if __name__ == "__main__":
    run_pipeline()
    
