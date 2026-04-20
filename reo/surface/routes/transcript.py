import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/transcripts/{transcript_unique_id}")
async def get_transcript(transcript_unique_id: str):
    file_path = os.path.join("transcripts", transcript_unique_id)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                return HTMLResponse(content=file_handle.read(), status_code=200)
        except Exception as error:
            raise HTTPException(status_code=500, detail="Internal Server Error") from error

    raise HTTPException(status_code=404, detail="Transcript not found")
