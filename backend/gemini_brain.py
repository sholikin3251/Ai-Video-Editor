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

    # 1. ATURAN (System Instruction) - Yang tadi kita update
    system_instruction = """
    Kamu adalah Editor Video Profesional.
    Tugas: Pilih momen terbaik dari video ini.
    
    ATURAN WAJIB (STRICT RULES):
    1. Durasi setiap potongan (segment) MINIMAL harus 3 DETIK. Jangan kurang dari itu.
    2. Jangan memotong kalimat orang di tengah jalan. Pastikan dialog utuh.
    3. Hindari potongan 'glitch' yang terlalu cepat.
    4. Gabungkan beberapa momen kecil menjadi satu segmen panjang jika berdekatan.
    
    Output HANYA JSON.
    """
    
    # 2. PERINTAH (Prompt) <--- BAGIAN INI YANG HILANG DI KODEMU
    prompt = """
    Analisis video ini. Berikan JSON berisi segmen terbaik.
    Format: {"segments": [{"start": 0.0, "end": 5.0, "description": "..."}]}
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