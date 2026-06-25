import os
import sys
import requests
import google.generativeai as genai

# --- حماية نهائية لاستيراد المكتبات ---
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.audio.io.AudioFileClip import AudioFileClip

# إعداد مفتاح Gemini
genai.configure(api_key=os.getenv("GEMINI_KEY"))

def run_pipeline():
    try:
        print("🚀 بدء تشغيل البوت...")
        
        # استخدام نموذج gemini-1.5-flash بدون بادئة models/
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # تجربة الاتصال
        test_res = model.generate_content("اكتب كلمة 'تم الاتصال بنجاح'")
        print(f"✅ Gemini: {test_res.text}")
        
        # استدعاء المحركات الخاصة بك
        from fal_engine import generate_image
        from pixverse_engine import animate_image
        
        # ... بقية المنطق الخاص بك ...
        
        print("✅ تم التنفيذ بنجاح!")
            
    except Exception as e:
        print(f"❌ فشل البوت بسبب: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
        
