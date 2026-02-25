# GenAI-Shorts-Maker
An automated AI Shorts generator built with Python. This AI-driven pipeline orchestrates Google Gemini for scripting, Edge-TTS for voiceovers, and Hugging Face's SDXL for contextual 3D image generation. Finally, MoviePy handles vertical cropping and Ken Burns cinematic zoom animations to assemble bizarre, highly engaging 30-second videos
An end-to-end Python pipeline that automatically generates bizarre, fascinating, 30-second vertical videos from a single text prompt.

This project orchestrates multiple AI models to write the script, generate a voiceover, create contextual images, and assemble everything into a final MP4 complete with Ken Burns zoom animations—perfect for YouTube Shorts, TikTok, or Instagram Reels.

✨ Features
AI Scripting: Uses Google Gemini to write perfectly timed, highly detailed scripts and visual prompts.

Text-to-Speech: Uses edge-tts for high-quality, natural-sounding voiceovers.

AI Image Generation: Integrates Hugging Face's Stable Diffusion XL to generate high-fidelity, contextual visuals for each scene.

Automated Video Assembly: Uses moviepy to resize, crop to 9:16 vertical format, add cinematic zoom animations, and stitch the audio and video together.
