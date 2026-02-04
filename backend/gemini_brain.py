import os
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv
from editor_engine import proses_video_otomatis  # <--- Kita import mesin pemotongnya

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_video_with_gemini(video_path):
    print(f"🤖 AI sedang menganalisis video: {video_path}...")
    
    # Upload Video
    video_file = genai.upload_file(path=video_path)
    
    while video_file.state.name == "PROCESSING":
        print("⏳ Menunggu video diproses oleh Google...")
        time.sleep(2)
        video_file = genai.get_file(video_file.name)
# 1. ATURAN (System Instruction) - MODE VIRAL
    system_instruction = """
    Kamu adalah Editor TikTok/Reels Profesional yang ahli membuat konten viral.
    Tugas: Ubah video mentah ini menjadi konten pendek yang menarik (Short-form content).
    
    STRATEGI EDITING (WAJIB):
    1. THE HOOK: Detik-detik pertama HARUS bagian paling menarik/lucu/mengejutkan untuk menahan penonton.
    2. FAST PACING: Buang semua jeda diam (dead air). Penonton milenial mudah bosan.
    3. DURASI: Total video hasil edit idealnya antara 15 - 60 detik.
    4. KONTEKS: Pastikan urutan cerita tetap masuk akal walau dipotong cepat.
    
    Output HANYA JSON.
    """
    
    # 2. PERINTAH (Prompt)
    prompt = """
    Analisis video ini. Berikan timeline editing untuk format Shorts/Reels.
    Format JSON: {"segments": [{"start": 0.0, "end": 3.5, "description": "Hook: Intro yang bikin penasaran"}, ...]}
    """
    # 3. Model Configuration
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest", 
        system_instruction=system_instruction
    )

    # 4. Generate Content (Disini dia memanggil variabel 'prompt')
    response = model.generate_content(
        [video_file, prompt],
        generation_config={"response_mime_type": "application/json"}
    )

    genai.delete_file(video_file.name)
    return json.loads(response.text)