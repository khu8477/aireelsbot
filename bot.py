import os
import requests
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips

# إعدادات FFmpeg
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# المفاتيح
GEMINI_KEY = os.getenv("GEMINI_KEY")
FAL_KEY = os.getenv("FAL_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def generate_image(prompt):
    # توليد صورة باستخدام Fal AI (Flux)
    url = "https://fal.run/fal-ai/flux/dev"
    headers = {"Authorization": f"Bearer {FAL_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "image_size": "landscape_16_9"}
    response = requests.post(url, headers=headers, json=payload)
    return response.json().get('images', [{}])[0].get('url')

def generate_video_from_image(image_url):
    # تحويل الصورة إلى فيديو (5 ثواني) باستخدام Stable Video Diffusion
    url = "https://fal.run/fal-ai/stable-video-diffusion"
    headers = {"Authorization": f"Bearer {FAL_KEY}", "Content-Type": "application/json"}
    payload = {"image_url": image_url, "motion_bucket_id": 127}
    response = requests.post(url, headers=headers, json=payload)
    video_url = response.json().get('video', {}).get('url')
    
    # تحميل الفيديو مؤقتاً
    video_data = requests.get(video_url).content
    filename = "clip.mp4"
    with open(filename, "wb") as f: f.write(video_data)
    return filename

def main():
    print("🚀 بدء العمل...")
    # 1. توليد 5 مطالبات (Prompts) للقصة
    prompts = ["مشهد 1", "مشهد 2", "مشهد 3", "مشهد 4", "مشهد 5"]
    clips = []
    
    for p in prompts:
        img_url = generate_image(f"cinematic shot of {p}")
        clip_path = generate_video_from_image(img_url)
        clips.append(VideoFileClip(clip_path))
    
    # 2. دمج الفيديوهات
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile("final_story.mp4", fps=24)
    print("✅ تم إنشاء الفيديو النهائي!")

if __name__ == "__main__":
    main()
    
