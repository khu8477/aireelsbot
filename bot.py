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

# إعداد Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

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
    if not FB_TOKEN or not FB_PAGE_ID:
        print("❌ بيانات فيسبوك ناقصة في الـ Secrets.")
        return
    url = f"https://graph.facebook.com/{FB_PAGE_ID}/videos"
    data = {"access_token": FB_TOKEN, "description": "قصة جديدة تم توليدها بالذكاء الاصطناعي! 🤖✨"}
    with open(video_path, 'rb') as f:
        files = {"file": f}
        response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        print("✅ تم النشر على فيسبوك بنجاح!")
    else:
        print(f"❌ خطأ في النشر على فيسبوك: {response.text}")

def main():
    prompts = ["غابة مسحورة", "بطل يبحث عن كنز", "كهف مظلم", "شروق الشمس", "احتفال بالنجاح"]
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
        print("✅ تم إنشاء الفيديو، جاري النشر...")
        post_to_facebook("final_story.mp4")
    else:
        print("❌ لم يتم توليد أي محتوى.")

if __name__ == "__main__":
    main()
    
