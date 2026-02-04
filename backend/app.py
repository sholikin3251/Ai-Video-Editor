from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import shutil # Kita butuh ini buat copy file
from werkzeug.utils import secure_filename
from gemini_brain import analyze_video_with_gemini
from editor_engine import proses_video_otomatis

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['video']
    if file.filename == '': return jsonify({"error": "No filename"}), 400

    if file:
        try:
            # 1. Simpan Video Asli
            original_name = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{unique_id}_{original_name}"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            # 2. AI Process
            print("🧠 AI Analyzing...")
            try:
                data_edit = analyze_video_with_gemini(input_path)
            except Exception as e:
                print(f"⚠️ AI Skip: {e}")
                data_edit = {"segments": []}

            # 3. Render
            output_filename = f"edited_{filename}"
            output_path = os.path.join(app.config['RESULTS_FOLDER'], output_filename)
            
            print("✂️ Rendering...")
            final_path = proses_video_otomatis(input_path, output_path, data_edit)

            # 4. Validasi Final
            final_name = os.path.basename(final_path)
            
            # Jika render gagal atau file hasil 0 bytes, kembalikan file asli
            if final_path == input_path or os.path.getsize(final_path) < 1000:
                print("⚠️ Menggunakan file asli karena render gagal/kosong.")
                # Copy file asli ke results folder biar bisa didownload
                fallback_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
                shutil.copy(input_path, fallback_path)
                final_name = filename
            
            return jsonify({
                "message": "Sukses",
                "download_url": f"http://localhost:5000/download/{final_name}",
                "ai_analysis": data_edit
            })

        except Exception as e:
            print(f"❌ Error: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)