import os
import sys
import requests
import google.generativeai as genai

# --- حماية نهائية لاستيراد المكتبات ---
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
except Exception:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        from moviepy.audio.io.AudioFileClip import AudioFileClip
    except Exception as e:
        print(f"Error loading moviepy: {e}")
        sys.exit(1)

# إعداد مفتاح Gemini
genai.configure(api_key=os.getenv("GEMINI_KEY"))

def run_pipeline():
    try:
        print("🚀 بدء تشغيل البوت...")
        
        # استدعاء المحركات (يجب أن تكون في نفس المجلد)
        from fal_engine import generate_image
        from pixverse_engine import animate_image
        
        # 1. إنشاء السكربت
        model = genai.GenerativeModel('gemini-1.5-flash')
        script = model.generate_content("اكتب قصة فواكه من 3 مشاهد، وصف بالإنجليزية لكل مشهد.").text
        
        # 2. التوليد
        images = [generate_image(f"Scene {i}") for i in range(3)]
        scenes = [animate_image(img) for img in images]
        
        # 3. المونتاج
        clips = [VideoFileClip(s).set_duration(5) for s in scenes]
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile("final_story.mp4", codec="libx264")
        
        print("✅ تم بنجاح!")
            
    except Exception as e:
        print(f"❌ فشل البوت بسبب: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
    
