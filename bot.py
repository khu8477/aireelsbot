import os
import asyncio
import requests
import edge_tts
import google.generativeai as genai

# استيراد آمن للمكتبات
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
except ImportError:
    # هذا السطر للتعامل مع النسخ الحديثة من moviepy
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

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, "ar-SA-ZariNeural")
    await communicate.save("story_audio.mp3")

def run_pipeline():
    try:
        send_telegram("🚀 البوت بدأ العمل - جاري إنتاج القصة...")
        
        # 1. إنشاء السكربت
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "اكتب قصة فواكه قصيرة من 5 مشاهد باللغة العربية، واكتب وصفاً (Prompt) لكل مشهد بالإنجليزية."
        script = model.generate_content(prompt).text
        
        # 2. توليد الصوت
        asyncio.run(generate_voice(script))
        
        # 3. استيراد المحركات
        from fal_engine import generate_image
        from pixverse_engine import animate_image
        
        # 4. المونتاج
        images = [generate_image(f"Scene {i}") for i in range(5)]
        scenes = [animate_image(img) for img in images]
        
        clips = [VideoFileClip(s).set_duration(5) for s in scenes]
        final = concatenate_videoclips(clips, method="compose")
        final = final.set_audio(AudioFileClip("story_audio.mp3"))
        final.write_videofile("final_story.mp4", fps=24, codec="libx264", audio_codec="aac")
        
        # 5. النشر (محاكاة)
        send_telegram("✅ تم إنتاج الفيديو بنجاح!")
            
    except Exception as e:
        send_telegram(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    run_pipeline()
    
