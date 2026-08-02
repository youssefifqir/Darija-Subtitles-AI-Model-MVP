from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse

from app.config import UPLOADS_DIR
from app.schemas import JobDetail, SegmentUpdate, UrlIngestRequest
from app.services import jobs, media
from app.services.subtitles import to_srt, to_vtt, to_txt

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobDetail)
async def create_job_from_upload(file: UploadFile = File(...)):
    job_id = jobs.create_job(media_filename=file.filename)
    ext = Path(file.filename).suffix or ".bin"
    dest = UPLOADS_DIR / f"{job_id}_source{ext}"
    with open(dest, "wb") as f:
        f.write(await file.read())

    jobs.submit(job_id, dest)
    return jobs.get_job(job_id)


@router.post("/from-url", response_model=JobDetail)
async def create_job_from_url(body: UrlIngestRequest):
    job_id = jobs.create_job(media_filename=body.url)
    try:
        source_path = media.download_from_url(body.url, UPLOADS_DIR, job_id)
    except media.MediaError as e:
        raise HTTPException(status_code=400, detail=str(e))

    jobs.submit(job_id, source_path)
    return jobs.get_job(job_id)


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(job_id: str):
    job = jobs.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@router.get("/{job_id}/media")
async def get_job_media(job_id: str):
    matches = list(UPLOADS_DIR.glob(f"{job_id}_source*"))
    if not matches:
        raise HTTPException(status_code=404, detail="source media not found")
    return FileResponse(matches[0])


@router.patch("/{job_id}/segments/{segment_id}")
async def update_segment(job_id: str, segment_id: int, body: SegmentUpdate):
    job = jobs.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    seg = jobs.update_segment_text(job_id, segment_id, body.text)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    return seg


@router.get("/{job_id}/export/{fmt}")
async def export_job(job_id: str, fmt: str):
    job = jobs.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != "done":
        raise HTTPException(status_code=409, detail=f"job not finished (status={job.status})")

    builders = {"srt": to_srt, "vtt": to_vtt, "txt": to_txt}
    if fmt not in builders:
        raise HTTPException(status_code=400, detail="fmt must be one of: srt, vtt, txt")

    content = builders[fmt](job.segments)
    media_type = "text/plain"
    return PlainTextResponse(
        content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{job_id}.{fmt}"'},
    )
