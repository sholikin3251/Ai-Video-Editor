import { useState } from "react";
import axios from "axios";
import "./App.css"; // Kita akan perbagus CSS-nya nanti

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [status, setStatus] = useState("");
  const [analysis, setAnalysis] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setVideoUrl("");
    setStatus("");
  };

  const handleUpload = async () => {
    if (!file) return alert("Pilih video dulu dong!");

    const formData = new FormData();
    formData.append("video", file);

    setLoading(true);
    setStatus("🚀 Sedang mengupload video ke server...");

    try {
      // 1. Upload & Proses di Backend
      // Nanti status akan berubah seiring proses backend (simulasi)
      setTimeout(() => setStatus("🧠 AI sedang menonton videomu..."), 2000);
      setTimeout(() => setStatus("✂️ Sedang memotong momen terbaik..."), 8000);

      const response = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        },
      );

      // 2. Sukses
      setVideoUrl(response.data.download_url);
      setAnalysis(response.data.ai_analysis);
      setStatus("✅ Selesai! Video viralmu sudah jadi.");
    } catch (error) {
      console.error(error);
      setStatus(
        "❌ Yah, error: " + (error.response?.data?.error || error.message),
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>✨ AI Video Editor Viral</h1>
      <p>Upload video mentah, biarkan AI membuatnya kekinian!</p>

      <div className="upload-box">
        <input type="file" accept="video/*" onChange={handleFileChange} />

        <button
          onClick={handleUpload}
          disabled={loading || !file}
          className={loading ? "btn-loading" : ""}
        >
          {loading ? "Sedang Memproses..." : "Buat Video Viral 🚀"}
        </button>
      </div>

      {/* Status Loading */}
      {status && <div className="status-text">{status}</div>}

      {loading && <div className="loader"></div>}

      {/* Hasil Video */}
      {videoUrl && (
        <div className="result-section">
          <h2>🎬 Hasil Edit AI:</h2>
          <video
            controls
            src={videoUrl}
            width="100%"
            className="video-player"
          ></video>

          <div className="download-btn-area">
            <a href={videoUrl} download className="btn-download">
              ⬇️ Download Video
            </a>
          </div>

          {/* Menampilkan Analisis AI */}
          <div className="ai-logs">
            <h3>📝 Catatan Editor AI:</h3>
            <pre>{JSON.stringify(analysis, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
