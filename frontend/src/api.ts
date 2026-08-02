export interface Segment {
  id: number;
  start: number;
  end: number;
  text: string;
  edited: boolean;
}

export interface JobDetail {
  id: string;
  status: "queued" | "processing" | "done" | "error";
  progress: string;
  error?: string | null;
  media_filename?: string | null;
  segments: Segment[];
}

const BASE = "/api/jobs";

export async function createJobFromFile(file: File): Promise<JobDetail> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(BASE, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createJobFromUrl(url: string): Promise<JobDetail> {
  const res = await fetch(`${BASE}/from-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJob(jobId: string): Promise<JobDetail> {
  const res = await fetch(`${BASE}/${jobId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateSegment(jobId: string, segmentId: number, text: string): Promise<Segment> {
  const res = await fetch(`${BASE}/${jobId}/segments/${segmentId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function mediaUrl(jobId: string): string {
  return `${BASE}/${jobId}/media`;
}

export function exportUrl(jobId: string, fmt: "srt" | "vtt" | "txt"): string {
  return `${BASE}/${jobId}/export/${fmt}`;
}
