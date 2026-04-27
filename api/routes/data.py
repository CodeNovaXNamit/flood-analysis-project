from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from api.database import create_run, get_latest_successful_run, get_run, list_runs, update_run
from api.pipeline import build_artifact_paths, run_pipeline, utc_now_iso


router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


def _serialize_run(record: dict | None) -> dict | None:
    if record is None:
        return None
    response = dict(record)
    response["summary"] = response.pop("summary_json", None)
    if response.get("run_id"):
        response["download_url"] = f"/api/pipeline/runs/{response['run_id']}/download"
    result_path = response.get("final_output_path")
    if response.get("status") == "completed" and result_path and Path(result_path).exists():
        response["result_points"] = pd.read_csv(result_path).round(6).to_dict(orient="records")
    else:
        response["result_points"] = []
    return response


@router.get("/runs")
def list_pipeline_runs(limit: int = 20) -> dict:
    return {"runs": [_serialize_run(run) for run in list_runs(limit=limit)]}


@router.get("/runs/latest")
def latest_pipeline_run() -> dict:
    run = get_latest_successful_run()
    if run is None:
        return {"run": None}
    return {"run": _serialize_run(run)}


@router.get("/runs/{run_id}")
def get_pipeline_run(run_id: str) -> dict:
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Pipeline run not found.")
    return {"run": _serialize_run(run)}


@router.get("/runs/{run_id}/download")
def download_pipeline_output(run_id: str) -> FileResponse:
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Pipeline run not found.")
    if run["status"] != "completed" or not run.get("final_output_path"):
        raise HTTPException(status_code=409, detail="Pipeline run has no downloadable output yet.")
    file_path = Path(run["final_output_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Output file is missing on disk.")
    return FileResponse(path=file_path, media_type="text/csv", filename=file_path.name)


@router.post("/runs")
async def create_pipeline_run(
    file: UploadFile = File(...),
    scenario_name: str | None = Form(default=None),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    run_id = str(uuid4())
    resolved_name = (scenario_name or Path(file.filename).stem).strip() or "uploaded-scenario"
    artifacts = build_artifact_paths(run_id=run_id, scenario_name=resolved_name, filename=file.filename)

    contents = await file.read()
    artifacts.upload_path.write_bytes(contents)

    timestamp = utc_now_iso()
    create_run(
        {
            "run_id": run_id,
            "scenario_name": resolved_name,
            "uploaded_filename": file.filename,
            "status": "processing",
            "created_at": timestamp,
            "updated_at": timestamp,
            "input_rows": None,
            "interpolated_rows": None,
            "output_rows": None,
            "latest_prediction_date": None,
            "upload_path": str(artifacts.upload_path),
            "interpolated_path": str(artifacts.interpolated_path),
            "enriched_path": str(artifacts.enriched_path),
            "predictions_path": str(artifacts.predictions_path),
            "final_output_path": str(artifacts.final_output_path),
            "summary_json": None,
            "error_message": None,
        }
    )

    try:
        result = run_pipeline(artifacts.upload_path, artifacts)
        update_run(
            run_id,
            {
                "status": "completed",
                "updated_at": utc_now_iso(),
                "input_rows": result["input_rows"],
                "interpolated_rows": result["interpolated_rows"],
                "output_rows": result["output_rows"],
                "latest_prediction_date": result["latest_prediction_date"],
                "summary_json": result["summary"],
            },
        )
    except Exception as exc:
        update_run(
            run_id,
            {
                "status": "failed",
                "updated_at": utc_now_iso(),
                "error_message": str(exc),
            },
        )
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc

    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=500, detail="Pipeline completed but run record could not be loaded.")

    payload = _serialize_run(run)
    payload["result_points"] = result["final_output"]
    return {"run": payload}
