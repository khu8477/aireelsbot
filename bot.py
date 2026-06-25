import os
import sys
import google.generativeai as genai

# --- حماية استيراد moviepy ---
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.audio.io.AudioFileClip import AudioFileClip

# إعداد Gemini (اسم النموذج مصحح لتجنب خطأ 404)
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def run_pipeline():
    try:
        print("🚀 البوت بدأ العمل بنجاح...")
        # تجربة اتصال سريعة
        res = model.generate_content("Hello")
        print("✅ اتصال Gemini ناجح!")
        
        # --- بقية المنطق الخاص بك هنا ---
        
    except Exception as e:
        print(f"❌ فشل البوت: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
    
