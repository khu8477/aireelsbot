import os
import requests
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips

# إعدادات البيئة
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# جلب المفاتيح
GEMINI_KEY = os.getenv("GEMINI_KEY")
FAL_KEY = os.getenv("FAL_KEY")
FB_TOKEN = os.getenv("FB_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def post_to_facebook(video_path):
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/videos"
    files = {"file": open(video_path, 'rb')}
    data = {"access_token": FB_TOKEN, "description": "قصة جديدة تم توليدها بالذكاء الاصطناعي 🤖✨"}
    response = requests.post(url, data=data, files=files)
    return response.status_code == 200

def main():
    try:
        send_telegram("🚀 البوت بدأ العمل الآن...")
        
        # [هنا تضع منطق توليد الصور والفيديو الخاص بك]
        # ...
        
        # بعد انتهاء توليد الفيديو final_story.mp4:
        if post_to_facebook("final_story.mp4"):
            send_telegram("✅ تم النشر على فيسبوك بنجاح!")
        else:
            send_telegram("⚠️ فشل النشر على فيسبوك.")
            
    except Exception as e:
        send_telegram(f"❌ حدث خطأ فادح: {str(e)}")

if __name__ == "__main__":
    main()
    
