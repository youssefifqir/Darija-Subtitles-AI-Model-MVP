from typing import Literal, Optional
from pydantic import BaseModel


class Segment(BaseModel):
    id: int
    start: float  # seconds
    end: float    # seconds
    text: str
    edited: bool = False


class JobStatus(BaseModel):
    id: str
    status: Literal["queued", "processing", "done", "error"]
    progress: str = ""
    error: Optional[str] = None
    media_filename: Optional[str] = None


class JobDetail(JobStatus):
    segments: list[Segment] = []


class UrlIngestRequest(BaseModel):
    url: str


class SegmentUpdate(BaseModel):
    text: str
