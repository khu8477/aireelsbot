import os
import requests
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips

# إعدادات النظام
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# جلب المفاتيح من متغيرات البيئة
GEMINI_KEY = os.getenv("GEMINI_KEY")
FAL_KEY = os.getenv("FAL_KEY")
FB_TOKEN = os.getenv("FB_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def send_telegram_msg(text):
    """إرسال رسالة نصية لتلغرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def send_to_telegram(video_path):
    """إرسال الفيديو النهائي لتلغرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video:
        files = {'video': video}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': "🤖 تم إنشاء القصة ونشرها بنجاح!"}
        requests.post(url, data=data, files=files)

def generate_image(prompt):
    url = "https://fal.run/fal-ai/flux/dev"
    headers = {"Authorization": f"Bearer {FAL_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "image_size": "landscape_16_9"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get('images', [{}])[0].get('url')
    except Exception as e:
        print(f"خطأ في توليد الصورة: {e}")
        return None

def generate_video_from_image(image_url):
    url = "https://fal.run/fal-ai/stable-video-diffusion"
    headers = {"Authorization": f"Bearer {FAL_KEY}", "Content-Type": "application/json"}
    payload = {"image_url": image_url, "motion_bucket_id": 127}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        video_url = response.json().get('video', {}).get('url')
        video_data = requests.get(video_url).content
        filename = "temp_clip.mp4"
        with open(filename, "wb") as f: f.write(video_data)
        return filename
    except Exception as e:
        print(f"خطأ في توليد الفيديو: {e}")
        return None

def post_to_facebook(video_path):
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/videos"
    data = {"access_token": FB_TOKEN, "description": "قصة جديدة من إبداع الذكاء الاصطناعي 🚀"}
    with open(video_path, 'rb') as f:
        files = {"file": f}
        response = requests.post(url, data=data, files=files)
    return response.status_code == 200

def main():
    send_telegram_msg("🚀 البوت بدأ العمل الآن...")
    prompts = ["غابة خيالية", "بطل يكتشف سر", "مغامرة في الصحراء", "شروق الشمس الساحر", "نهاية سعيدة"]
    clips = []
    
    for p in prompts:
        img_url = generate_image(f"cinematic shot of {p}")
        if img_url:
            clip_path = generate_video_from_image(img_url)
            if clip_path:
                clips.append(VideoFileClip(clip_path))
    
    if clips:
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile("final_story.mp4", fps=24)
        
        # النشر على فيسبوك
        if post_to_facebook("final_story.mp4"):
            send_telegram_msg("✅ تم النشر على فيسبوك بنجاح!")
        else:
            send_telegram_msg("⚠️ تم إنشاء الفيديو ولكن فشل النشر على فيسبوك.")
            
        # إرسال الفيديو لتلغرام
        send_to_telegram("final_story.mp4")
    else:
        send_telegram_msg("❌ فشلت العملية: لم يتم إنتاج أي فيديو.")

if __name__ == "__main__":
    main()
    
