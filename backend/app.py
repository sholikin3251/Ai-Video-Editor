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

            # 2. Panggil AI (Otak)
            print("🧠 Sedang meminta instruksi AI...")
            data_edit = analyze_video_with_gemini(input_path)

            # 3. Panggil Editor (Otot)
            output_filename = f"edited_{filename}"
            output_path = os.path.join(app.config['RESULTS_FOLDER'], output_filename)
            
            print("✂️ Sedang memotong video...")
            final_video_path = proses_video_otomatis(input_path, output_path, data_edit)

            if final_video_path:
                # Kirim URL download ke Frontend
                return jsonify({
                    "message": "Sukses!",
                    "download_url": f"http://localhost:5000/download/{output_filename}",
                    "ai_analysis": data_edit
                })
            else:
                return jsonify({"error": "Gagal mengedit video"}), 500

        except Exception as e:
            print(f"❌ Error: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    # Endpoint agar Frontend bisa mendownload hasil
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)