from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "outputs" / "pipeline" / "pipeline.db"


def _ensure_parent() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    _ensure_parent()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                scenario_name TEXT NOT NULL,
                uploaded_filename TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                input_rows INTEGER,
                interpolated_rows INTEGER,
                output_rows INTEGER,
                latest_prediction_date TEXT,
                upload_path TEXT,
                interpolated_path TEXT,
                enriched_path TEXT,
                predictions_path TEXT,
                final_output_path TEXT,
                summary_json TEXT,
                error_message TEXT
            )
            """
        )


def create_run(record: dict[str, Any]) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_id, scenario_name, uploaded_filename, status, created_at, updated_at,
                input_rows, interpolated_rows, output_rows, latest_prediction_date,
                upload_path, interpolated_path, enriched_path, predictions_path,
                final_output_path, summary_json, error_message
            ) VALUES (
                :run_id, :scenario_name, :uploaded_filename, :status, :created_at, :updated_at,
                :input_rows, :interpolated_rows, :output_rows, :latest_prediction_date,
                :upload_path, :interpolated_path, :enriched_path, :predictions_path,
                :final_output_path, :summary_json, :error_message
            )
            """,
            {
                **record,
                "summary_json": json.dumps(record.get("summary_json")) if record.get("summary_json") is not None else None,
            },
        )


def update_run(run_id: str, updates: dict[str, Any]) -> None:
    if not updates:
        return
    payload = dict(updates)
    if "summary_json" in payload:
        payload["summary_json"] = json.dumps(payload["summary_json"]) if payload["summary_json"] is not None else None
    assignments = ", ".join(f"{key} = :{key}" for key in payload)
    payload["run_id"] = run_id
    with get_connection() as conn:
        conn.execute(f"UPDATE pipeline_runs SET {assignments} WHERE run_id = :run_id", payload)


def _deserialize(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    record = dict(row)
    if record.get("summary_json"):
        record["summary_json"] = json.loads(record["summary_json"])
    else:
        record["summary_json"] = None
    return record


def get_run(run_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM pipeline_runs WHERE run_id = ?", (run_id,)).fetchone()
    return _deserialize(row)


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_deserialize(row) for row in rows]


def get_latest_successful_run() -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM pipeline_runs
            WHERE status = 'completed'
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()
    return _deserialize(row)
