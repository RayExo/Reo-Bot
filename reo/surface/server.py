from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from reo.surface.routes import dashboard, generate, transcript
from reo.surface.runtime import bind_bot

app = FastAPI(title="REO Surface", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard", status_code=303)


app.include_router(transcript.router)
app.include_router(generate.router)
app.include_router(dashboard.router)
