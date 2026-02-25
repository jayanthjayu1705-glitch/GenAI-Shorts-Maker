import google.generativeai as genai
import edge_tts
import asyncio
import json
import requests
import os
# Notice we added CompositeVideoClip to the imports for the animation!
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip

# --- 1. CONFIGURATION & API KEYS ---
GEMINI_API_KEY = "Add your own API"
HUGGINGFACE_TOKEN = "Add your own API"

# Setup Folders
os.makedirs("assets", exist_ok=True)
os.makedirs("output", exist_ok=True)

# --- 2. THE BRAIN: Generate Script & Prompts (Gemini) ---
def generate_content(user_topic):
    print(f"🧠 Asking Gemini to write a script about: {user_topic}...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Create a 30-second YouTube Short script about: {user_topic}.
    Style: Like Zack D. Films (bizarre science/anatomy facts, slightly gross but fascinating).
    Output ONLY valid JSON format. No markdown, no extra text.
    Format exactly like this:
    {{
      "script": "The 30-second spoken script.",
      "visual_prompts": [
        "Scene 1: 3D render, macro photography, fleshy, medical animation style, highly detailed, Unreal Engine 5",
        "Scene 2: (Add another specific 3D style prompt describing the next scene)",
        "Scene 3: (Add another)",
        "Scene 4: (Add another)"
      ]
    }}
    """
    
    response = model.generate_content(prompt)
    try:
        raw_json = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw_json)
        return data['script'], data['visual_prompts']
    except Exception as e:
        print(f"Error parsing JSON: {e}\nRaw output: {response.text}")
        return None, None

# --- 3. THE VOICE: Text-to-Speech (Edge-TTS) ---
async def generate_audio(script_text, output_path="assets/voiceover.mp3"):
    print("🎙️ Generating voiceover using Edge-TTS...")
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save(output_path)
    return output_path

# --- 4. THE VISUALS: AI Image Generation (Hugging Face) ---
def generate_images(prompts):
    print("🎨 Generating 3D images via Hugging Face...")
    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    
    image_paths = []
    for i, prompt in enumerate(prompts):
        print(f"   -> Generating Image {i+1}...")
        payload = {"inputs": prompt}
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            image_path = f"assets/scene_{i+1}.png"
            with open(image_path, "wb") as f:
                f.write(response.content)
            image_paths.append(image_path)
        else:
            print(f"Failed to generate image {i+1}: {response.text}")
            
    return image_paths

# --- 5. THE ASSEMBLY: Adding Animation & Stitching (MoviePy) ---
def build_video(image_paths, audio_path, output_filename="output/final_short.mp4"):
    print("🎬 Assembling the final video with ANIMATION effects...")
    
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    time_per_image = audio_duration / len(image_paths)
    
    video_clips = []
    for img_path in image_paths:
        # 1. Load the image and set how long it stays on screen
        clip = ImageClip(img_path).set_duration(time_per_image)
        
        # 2. Resize to fill the vertical height (1920) so there are no black bars
        clip = clip.resize(height=1920)
        
        # 3. Crop the center to exactly 1080 wide to fit the YouTube Shorts ratio
        if clip.w > 1080:
            x_center = clip.w / 2
            clip = clip.crop(x1=x_center-540, y1=0, x2=x_center+540, y2=1920)
        
        # 4. THE ANIMATION HACK: Add a slow, cinematic zoom-in effect (Ken Burns)
        # This function slowly scales the image up over time
        clip = clip.resize(lambda t: 1 + 0.03 * t)
        
        # 5. Lock the zooming image to the center of a 1080x1920 canvas so it doesn't drift
        clip = CompositeVideoClip([clip.set_position(('center', 'center'))], size=(1080, 1920))
        
        video_clips.append(clip)
        
    final_video = concatenate_videoclips(video_clips, method="compose")
    final_video = final_video.set_audio(audio_clip)
    
    # Exporting takes longer now because Python is rendering every single frame of the animation
    print("⏳ Rendering MP4... (This might take a few minutes because of the animation)")
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ DONE! Video saved to: {output_filename}")

# --- MAIN EXECUTION PIPELINE ---
async def main():
    topic = input("Enter a topic for your Zack D. Films style video (e.g., 'What happens if you swallow a spider?'): ")
    
    script, visual_prompts = generate_content(topic)
    
    if script and visual_prompts:
        print(f"\n--- GENERATED SCRIPT ---\n{script}\n------------------------\n")
        
        await generate_audio(script)
        image_paths = generate_images(visual_prompts)
        
        if len(image_paths) > 0:
            build_video(image_paths, "assets/voiceover.mp3")
        else:
            print("❌ Pipeline failed: No images were generated.")

if __name__ == "__main__":
    asyncio.run(main())
