import fal_client
def generate_image(prompt):
    handler = fal_client.submit("fal-ai/flux/schnell", arguments={"prompt": prompt, "image_size": "landscape_16_9"})
    return handler.get()['images'][0]['url']
  
