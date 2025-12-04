"""
FastAPI server that lets users upload a match video and receive per-player ratings.
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.pipeline.video_runner import run_video_analysis

app = FastAPI(title="Soccer Analytics API", version="0.1.0")

# Allow frontend dev servers to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_path: str = "yolov8n.pt",
    save_annotated: bool = False,
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    suffix = Path(file.filename).suffix or ".mp4"
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_video_path = Path(tmp.name)
    except Exception as exc:  # pragma: no cover - defensive only
        raise HTTPException(status_code=500, detail=f"Failed to persist upload: {exc}") from exc

    output_dir = Path("uploads") / temp_video_path.stem
    save_video_path = output_dir / "annotated.mp4" if save_annotated else None

    try:
        result = run_video_analysis(
            video_path=temp_video_path,
            model_path=model_path,
            output_dir=output_dir,
            save_video_path=save_video_path,
            display=False,
        )
    except Exception as exc:  # pragma: no cover - defensive only
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        background_tasks.add_task(temp_video_path.unlink)

    return {
        "metrics_path": str(result["metrics_path"]),
        "ratings_path": str(result["ratings_path"]),
        "annotated_video_path": str(result["annotated_video_path"]) if result["annotated_video_path"] else None,
        "ratings": result["ratings"],
        "metrics_summary": result.get("metrics_summary"),
        "rating_inputs": result.get("rating_inputs"),
    }
