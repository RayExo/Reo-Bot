from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/transcripts/{transcript_unique_id}")
async def get_transcript(transcript_unique_id: str):
    transcripts_dir = Path(__file__).resolve().parents[3] / "transcripts"
    file_path = transcripts_dir / transcript_unique_id

    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                return HTMLResponse(content=file_handle.read(), status_code=200)
        except Exception as error:
            raise HTTPException(status_code=500, detail="Internal Server Error") from error

    raise HTTPException(status_code=404, detail="Transcript not found")
