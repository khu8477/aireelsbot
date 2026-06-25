import os
import sys
import logging
import google.generativeai as genai

# إعداد السجلات لرؤية مكان الخطأ بدقة
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- حماية استيراد moviepy ---
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
except ImportError:
    logger.warning("اصدار moviepy يحتاج استيراداً خاصاً...")
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.audio.io.AudioFileClip import AudioFileClip

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_KEY"))

def run_pipeline():
    try:
        logger.info("🚀 بدء تشغيل البوت...")
        
        # تصحيح: استخدام اسم النموذج بدون كلمة 'models/' لتجنب خطأ 404
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # اختبار الاتصال
        response = model.generate_content("أهلاً")
        logger.info(f"✅ تم الاتصال بـ Gemini: {response.text[:20]}...")
        
        # استيراد محركاتك (تأكد من وجود هذه الملفات في المستودع)
        from fal_engine import generate_image
        from pixverse_engine import animate_image
        
        logger.info("✅ تم التنفيذ بنجاح!")
            
    except Exception as e:
        logger.error(f"❌ فشل البوت بسبب: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
    
