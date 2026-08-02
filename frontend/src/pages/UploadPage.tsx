import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createJobFromFile, createJobFromUrl } from "../api";

export default function UploadPage() {
  const navigate = useNavigate();
  const fileInput = useRef<HTMLInputElement>(null);
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setBusy(true);
    setError(null);
    try {
      const job = await createJobFromFile(file);
      navigate(`/job/${job.id}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function handleUrlSubmit() {
    if (!url.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const job = await createJobFromUrl(url.trim());
      navigate(`/job/${job.id}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container">
      <h1>Darija Subtitles — Demo</h1>
      <p>Upload a video/audio file, or paste a YouTube / TikTok / Instagram link.</p>

      <div
        className="dropzone"
        onClick={() => fileInput.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const file = e.dataTransfer.files?.[0];
          if (file) handleFile(file);
        }}
      >
        {busy ? "Uploading…" : "Click or drag a file here (MP4, MOV, MP3, WAV)"}
        <input
          ref={fileInput}
          type="file"
          accept="video/*,audio/*"
          style={{ display: "none" }}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </div>

      <div className="url-row">
        <input
          placeholder="https://youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={busy}
        />
        <button onClick={handleUrlSubmit} disabled={busy}>
          Process URL
        </button>
      </div>

      {error && <p className="error">{error}</p>}
    </div>
  );
}
