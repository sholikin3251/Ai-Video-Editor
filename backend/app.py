from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from gemini_brain import analyze_video_with_gemini
from editor_engine import proses_video_otomatis

app = Flask(__name__)
CORS(app) # Biar React bisa akses

# Konfigurasi Folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "Tidak ada file video"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    if file:
        try:
            # 1. Simpan Video Mentah
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            print(f"📥 File diterima: {filename}")

            # 2. Panggil AI
            print("🧠 Sedang meminta instruksi AI...")
            # Kita bungkus try-except biar kalau AI error, tetap lanjut
            try:
                data_edit = analyze_video_with_gemini(input_path)
            except Exception as e:
                print(f"⚠️ AI Error: {e}, menggunakan default.")
                data_edit = {"segments": []} # Default kosong

            # 3. Panggil Editor
            output_filename = f"edited_{filename}"
            output_path = os.path.join(app.config['RESULTS_FOLDER'], output_filename)
            
            print("✂️ Sedang memproses video...")
            final_path = proses_video_otomatis(input_path, output_path, data_edit)

            if final_path:
                # Cek apakah yang dikembalikan adalah file asli atau file edit
                final_filename = os.path.basename(final_path)
                
                # Jika file aslinya ada di folder uploads, tapi Flask butuh akses, 
                # kita harus pastikan endpoint download bisa mengaksesnya.
                # Sederhananya: Kita copy file final ke folder results jika belum ada disitu.
                if final_filename != output_filename:
                     # Ini artinya logic Fail-Safe berjalan (video asli dikembalikan)
                     import shutil
                     shutil.copy(input_path, output_path)
                     final_filename = output_filename

                return jsonify({
                    "message": "Sukses!",
                    "download_url": f"http://localhost:5000/download/{final_filename}",
                    "ai_analysis": data_edit
                })
            else:
                return jsonify({"error": "Gagal total memproses video"}), 500

        except Exception as e:
            print(f"❌ Server Error: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    # Endpoint agar Frontend bisa mendownload hasil
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)