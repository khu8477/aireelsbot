import os
import asyncio
import requests
import google.generativeai as genai

# --- حل نهائي لمشكلة الاستيراد ---
try:
    # الطريقة التقليدية
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
except ImportError:
    # الطريقة الحديثة (إذا فشلت الأولى)
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
        
        # 1. إنشاء السكربت
        model = genai.GenerativeModel('gemini-1.5-flash')
        script = model.generate_content("اكتب قصة فواكه من 3 مشاهد، وصف لكل مشهد بالإنجليزية.").text
        
        # 2. استيراد الأدوات (تأكد أن هذه الملفات موجودة في المجلد الرئيسي)
        from fal_engine import generate_image
        from pixverse_engine import animate_image
        
        # 3. توليد المحتوى
        images = [generate_image(f"Scene {i}") for i in range(3)]
        scenes = [animate_image(img) for img in images]
        
        # 4. المونتاج
        clips = [VideoFileClip(s).set_duration(5) for s in scenes]
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile("final_story.mp4", fps=24, codec="libx264")
        
        send_telegram("✅ تم إنتاج الفيديو بنجاح!")
            
    except Exception as e:
        send_telegram(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    run_pipeline()
    
