import os
import requests
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips

# إعدادات FFmpeg - تأكد من وجوده في المسار
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# جلب المفاتيح من متغيرات البيئة
GEMINI_KEY = os.getenv("GEMINI_KEY")
FAL_KEY = os.getenv("FAL_KEY")

# إعداد Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def generate_image(prompt):
    """توليد صورة باستخدام Fal AI"""
    url = "https://fal.run/fal-ai/flux/dev"
    headers = {"Authorization": f"Bearer {FAL_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "image_size": "landscape_16_9"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get('images', [{}])[0].get('url')
    except Exception as e:
        print(f"خطأ في توليد الصورة: {e}")
        return None

def generate_video_from_image(image_url):
    """تحويل الصورة إلى فيديو باستخدام Stable Video Diffusion"""
    url = "https://fal.run/fal-ai/stable-video-diffusion"
    headers = {"Authorization": f"Bearer {FAL_KEY}", "Content-Type": "application/json"}
    payload = {"image_url": image_url, "motion_bucket_id": 127}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        video_url = response.json().get('video', {}).get('url')
        
        # تحميل الفيديو محلياً للمعالجة
        video_data = requests.get(video_url).content
        filename = "temp_clip.mp4"
        with open(filename, "wb") as f:
            f.write(video_data)
        return filename
    except Exception as e:
        print(f"خطأ في توليد الفيديو: {e}")
        return None

def main():
    print("🚀 بدء تنفيذ مهمة توليد القصة والفيديو...")
    
    # 5 مشاهد للقصة
    prompts = ["غابة مسحورة", "بطل يبحث عن كنز", "كهف مظلم", "خروج الشمس", "احتفال بالنجاح"]
    clips = []
    
    for i, p in enumerate(prompts):
        print(f"--- جاري معالجة المشهد {i+1}: {p} ---")
        
        # 1. توليد الصورة
        img_url = generate_image(f"cinematic shot of {p}")
        if not img_url:
            print(f"تخطي المشهد {i+1} لعدم توفر الصورة.")
            continue
            
        # 2. توليد الفيديو
        clip_path = generate_video_from_image(img_url)
        if clip_path:
            try:
                clips.append(VideoFileClip(clip_path))
                print(f"تمت إضافة المشهد {i+1} بنجاح.")
            except Exception as e:
                print(f"خطأ عند معالجة الفيديو: {e}")
    
    # 3. دمج الفيديوهات النهائية
    if clips:
        print("🎬 جاري دمج المشاهد...")
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile("final_story.mp4", fps=24)
        print("✅ تم إنشاء الفيديو النهائي بنجاح: final_story.mp4")
    else:
        print("❌ فشلت العملية: لم يتم إنتاج أي فيديو.")

if __name__ == "__main__":
    main()
    
