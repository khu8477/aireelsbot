import requests, os
def animate_image(image_url):
    response = requests.post("https://api.pixverse.ai/v1/generate", 
                             json={"image_url": image_url, "motion_strength": 5},
                             headers={"Authorization": f"Bearer {os.getenv('PIXVERSE_KEY')}"})
    return response.json()['video_url']
  
