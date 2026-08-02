import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { getJob, updateSegment, mediaUrl, exportUrl, JobDetail } from "../api";

export default function ReviewPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<JobDetail | null>(null);
  const [activeSegment, setActiveSegment] = useState<number | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!jobId) return;
    let stop = false;

    async function poll() {
      const j = await getJob(jobId!);
      if (stop) return;
      setJob(j);
      if (j.status !== "done" && j.status !== "error") {
        setTimeout(poll, 1500);
      }
    }
    poll();
    return () => {
      stop = true;
    };
  }, [jobId]);

  function handleTimeUpdate() {
    if (!job || !videoRef.current) return;
    const t = videoRef.current.currentTime;
    const seg = job.segments.find((s) => t >= s.start && t <= s.end);
    setActiveSegment(seg ? seg.id : null);
  }

  async function handleSegmentEdit(segId: number, text: string) {
    if (!jobId) return;
    setJob((prev) =>
      prev
        ? { ...prev, segments: prev.segments.map((s) => (s.id === segId ? { ...s, text } : s)) }
        : prev
    );
  }

  async function handleSegmentBlur(segId: number, text: string) {
    if (!jobId) return;
    await updateSegment(jobId, segId, text);
  }

  function seekTo(start: number) {
    if (videoRef.current) videoRef.current.currentTime = start;
  }

  if (!job) return <div className="container">Loading…</div>;

  return (
    <div className="container">
      <h1>Review — {job.media_filename}</h1>

      {job.status !== "done" && (
        <div className="status-banner">
          Status: {job.status} — {job.progress}
        </div>
      )}
      {job.status === "error" && <p className="error">{job.error}</p>}

      <div className="review-layout">
        <div style={{ flex: 1 }}>
          {jobId && (
            <video ref={videoRef} src={mediaUrl(jobId)} controls onTimeUpdate={handleTimeUpdate} />
          )}
          {job.status === "done" && (
            <div className="export-row">
              <a href={exportUrl(jobId!, "srt")}><button>Export SRT</button></a>
              <a href={exportUrl(jobId!, "vtt")}><button>Export VTT</button></a>
              <a href={exportUrl(jobId!, "txt")}><button>Export TXT</button></a>
            </div>
          )}
        </div>

        <div className="segments">
          {job.segments.map((seg) => (
            <div
              key={seg.id}
              className={`segment ${activeSegment === seg.id ? "active" : ""}`}
              onClick={() => seekTo(seg.start)}
            >
              <div className="time">
                {seg.start.toFixed(1)}s → {seg.end.toFixed(1)}s {seg.edited ? "· edited" : ""}
              </div>
              <textarea
                dir="rtl"
                rows={2}
                value={seg.text}
                onChange={(e) => handleSegmentEdit(seg.id, e.target.value)}
                onBlur={(e) => handleSegmentBlur(seg.id, e.target.value)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
