import os, time, requests, random, subprocess, json
from datetime import datetime
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import *
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# قرا المفاتيح من GitHub Secrets
GEMINI_KEY = os.getenv("GEMINI_KEY")
FAL_KEY = os.getenv("FAL_KEY")
FB_TOKEN = os.getenv("FB_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def get_trend():
    send_telegram("🎬 Gemini كيقلب على الترند دابا...")
    prompt = "عطيني فكرة قصة قصيرة بالدارجة المغربية فيها 7 مشاهد، كل مشهد سطر واحد. موضوع: حاجة غريبة ولا مخيفة ولا مضحكة ترند دابا"
    response = model.generate_content(prompt)
    scenes = response.text.strip().split('\n')
    return [s for s in scenes if s][:7]

def generate_image(prompt, scene_num):
    send_telegram(f"🎨 كنصنع صورة المشهد {scene_num}/7...")
    url = "https://fal.ai/api/queue/flux/dev"
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    data = {"prompt": prompt + ", cinematic, 9:16, high quality", "image_size": "portrait_4_3"}
    r = requests.post(url, headers=headers, json=data)
    result = r.json()

    # تسنا حتى توجد الصورة
    while result['status']!= 'completed':
        time.sleep(3)
        r = requests.get(result['logs'][0]['url'], headers=headers)
        result = r.json()

    img_url = result['output']['url']
    img_path = f"scene{scene_num}.jpg"
    with open(img_path, 'wb') as f:
        f.write(requests.get(img_url).content)
    return img_path

def create_video(image_path, text, scene_num):
    send_telegram(f"🎞️ كنحول الصورة لفيديو {scene_num}/7...")
    tts = gTTS(text=text, lang='ar')
    audio_path = f"audio{scene_num}.mp3"
    tts.save(audio_path)

    audio = AudioFileClip(audio_path)
    img = ImageClip(image_path).set_duration(audio.duration)
    img = img.resize((1080, 1920)) # 9:16

    video = CompositeVideoClip([img])
    video = video.set_audio(audio)
    video_path = f"video{scene_num}.mp4"
    video.write_videofile(video_path, fps=24, codec='libx264')
    return video_path

def post_facebook(video_path, caption):
    send_telegram("📤 كننشر على Facebook...")
    url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/videos"
    files = {'file': open(video_path, 'rb')}
    data = {'access_token': FB_TOKEN, 'description': caption}
    r = requests.post(url, files=files, data=data)
    return r.json()

def main():
    send_telegram("🚀 البوت بدا الخدمة!")
    try:
        scenes = get_trend()
        video_clips = []

        for i, scene in enumerate(scenes, 1):
            img = generate_image(scene, i)
            vid = create_video(img, scene, i)
            video_clips.append(VideoFileClip(vid))

        final = concatenate_videoclips(video_clips, method="compose")
        final.write_videofile("final.mp4", fps=24)

        caption = "#قصة #ترند #المغرب"
        result = post_facebook("final.mp4", caption)

        if 'id' in result:
            send_telegram("✅ تم النشر بنجاح على Facebook!")
        else:
            send_telegram(f"❌ خطأ: {result}")

    except Exception as e:
        send_telegram(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    main()
