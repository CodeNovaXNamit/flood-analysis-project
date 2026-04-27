"""
Generate a professional PDF project report for the Flood Analysis Project.

This script creates a complete, submission-ready document using ReportLab.
It is intentionally self-contained so it can run without any project-specific
imports or environment variables.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT_FILE = Path("Flood_Analysis_Project_Documentation.pdf")


PROJECT_NAME = "Delhi Flood Intelligence Platform"
PROJECT_TAGLINE = (
    "An AI-assisted flood-risk analysis and scenario simulation platform "
    "for ward-level planning, operational response, and urban resilience."
)
AUTHOR = "Prepared by OpenAI Codex for CodeNovaXNamit"


def build_styles():
    """Create custom styles used throughout the document."""
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0B1F33"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtitleCustom",
            parent=styles["Heading2"],
            fontName="Helvetica",
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#36516B"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#0F3D63"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubsectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=colors.HexColor("#184E77"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#1F2933"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13,
            alignment=TA_LEFT,
            leftIndent=10,
            textColor=colors.HexColor("#1F2933"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallMuted",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5C6B7A"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeCaption",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.2,
            leading=12,
            textColor=colors.HexColor("#0F3D63"),
            spaceBefore=4,
            spaceAfter=4,
        )
    )
    return styles


def page_header_footer(canvas, doc):
    """Draw a simple professional header and footer on every page."""
    canvas.saveState()
    width, height = A4

    canvas.setStrokeColor(colors.HexColor("#B9C7D6"))
    canvas.line(doc.leftMargin, height - 1.3 * cm, width - doc.rightMargin, height - 1.3 * cm)

    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.HexColor("#0F3D63"))
    canvas.drawString(doc.leftMargin, height - 1.05 * cm, PROJECT_NAME)

    canvas.setFont("Helvetica", 8.2)
    canvas.setFillColor(colors.HexColor("#5C6B7A"))
    canvas.drawRightString(
        width - doc.rightMargin,
        height - 1.05 * cm,
        "Project Documentation",
    )

    canvas.setStrokeColor(colors.HexColor("#B9C7D6"))
    canvas.line(doc.leftMargin, 1.2 * cm, width - doc.rightMargin, 1.2 * cm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5C6B7A"))
    canvas.drawString(doc.leftMargin, 0.85 * cm, AUTHOR)
    canvas.drawRightString(width - doc.rightMargin, 0.85 * cm, f"Page {doc.page}")
    canvas.restoreState()


def p(text: str, styles, style_name: str = "BodyCustom"):
    return Paragraph(text, styles[style_name])


def section(title: str, styles):
    return Paragraph(title, styles["SectionTitle"])


def subsection(title: str, styles):
    return Paragraph(title, styles["SubsectionTitle"])


def bullets(items, styles):
    flow = []
    for item in items:
        flow.append(ListItem(Paragraph(item, styles["BulletCustom"])))
    return ListFlowable(flow, bulletType="bullet", leftIndent=16)


def code_block(code: str, styles):
    return Preformatted(
        code.strip(),
        ParagraphStyle(
            "CodeBlock",
            parent=styles["BodyCustom"],
            fontName="Courier",
            fontSize=8.1,
            leading=10,
            backColor=colors.HexColor("#F5F8FB"),
            borderWidth=0.5,
            borderColor=colors.HexColor("#D5E1EC"),
            borderPadding=6,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=4,
            spaceAfter=8,
        ),
    )


def table(data, col_widths=None):
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F3D63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FBFD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F8FB")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D3DF")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tbl


def build_story():
    styles = build_styles()
    story = []

    generated_on = datetime.now().strftime("%d %B %Y")

    # Title page
    story.append(Spacer(1, 4.8 * cm))
    story.append(Paragraph(PROJECT_NAME, styles["TitleCustom"]))
    story.append(Paragraph(PROJECT_TAGLINE, styles["SubtitleCustom"]))
    story.append(Spacer(1, 1.0 * cm))
    story.append(
        p(
            "Industry-level technical project report covering architecture, design, "
            "implementation, deployment, testing, and future roadmap.",
            styles,
            "SmallMuted",
        )
    )
    story.append(Spacer(1, 2.8 * cm))
    story.append(Paragraph("<b>Description</b>", styles["SubsectionTitle"]))
    story.append(
        p(
            "This document describes a flood-risk intelligence system built for urban "
            "authorities, emergency planners, and resilience teams. The platform combines "
            "data ingestion, machine learning inference, geospatial risk mapping, and a web "
            "dashboard for scenario-based flood forecasting in Delhi wards.",
            styles,
        )
    )
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(f"<b>Author</b>: {AUTHOR}", styles["BodyCustom"]))
    story.append(Paragraph(f"<b>Date</b>: {generated_on}", styles["BodyCustom"]))
    story.append(PageBreak())

    # 2. Abstract
    story.append(section("2. Abstract", styles))
    story.append(
        p(
            "The Delhi Flood Intelligence Platform is a decision-support system designed to "
            "transform rainfall observations and scenario uploads into coordinate-level flood-risk "
            "predictions and ward-level operational insights. The system exposes a FastAPI backend "
            "for scenario processing, uses a lightweight ensemble of machine learning models for "
            "risk estimation, stores run history in a local SQLite database, and provides a Next.js "
            "dashboard for visualization, hotspot inspection, and scenario uploads. The project is "
            "structured for academic submission as well as interview discussion because it combines "
            "data engineering, geospatial analytics, backend services, frontend product design, and "
            "deployment engineering in a single coherent platform.",
            styles,
        )
    )

    # 3. Problem Statement
    story.append(section("3. Problem Statement", styles))
    story.append(
        p(
            "Urban flood response typically suffers from fragmented data sources, delayed analysis, "
            "and limited ward-level visibility. Emergency teams often receive rainfall data, drainage "
            "context, and historical vulnerability indicators in separate silos. This slows down "
            "decision-making during high-rainfall events and makes it difficult to prioritize local "
            "response measures. The project addresses this gap by building a platform that standardizes "
            "rainfall inputs, interpolates them over a reference grid, enriches them with static spatial "
            "features, predicts proxy flood risk, and presents the result through an operational dashboard.",
            styles,
        )
    )
    story.append(
        bullets(
            [
                "Manual flood assessment is too slow for operational planning.",
                "Ward-level decision-makers need localized risk rather than city-wide averages.",
                "Multiple data formats make ingestion and analysis error-prone.",
                "Non-technical stakeholders need a visual workflow, not only CSV outputs.",
            ],
            styles,
        )
    )

    # 4. Objectives
    story.append(section("4. Objectives", styles))
    story.append(
        bullets(
            [
                "Provide a repeatable pipeline for converting rainfall scenario CSV files into flood-risk predictions.",
                "Expose a clean API for scenario upload, run tracking, and result download.",
                "Offer a geospatial dashboard for ward visualization and hotspot analysis.",
                "Maintain a lightweight architecture that is easy to run locally or through Docker.",
                "Support viva, interview, and project-submission use cases with explainable system design.",
            ],
            styles,
        )
    )

    # 5. System Overview
    story.append(section("5. System Overview", styles))
    story.append(
        p(
            "At a high level, the platform accepts rainfall observations or simulated rainfall scenarios, "
            "standardizes the schema, interpolates rainfall to a predefined model grid, generates inference "
            "features, merges static coordinate-level context, performs ensemble prediction, and stores "
            "artifacts for auditability. The frontend periodically queries the backend for the latest successful "
            "pipeline run and overlays risk outputs on top of ward or hotspot visualizations. This separation "
            "between presentation and computation keeps the system modular and production-friendly.",
            styles,
        )
    )

    # 6. Architecture
    story.append(section("6. Architecture", styles))
    story.append(subsection("6.1 Architectural Style", styles))
    story.append(
        p(
            "The implementation follows a modular monolith pattern with clearly separated frontend, backend, "
            "data-processing, and model layers. While not decomposed into independently deployed microservices, "
            "the system uses API boundaries and file/module boundaries that allow future service extraction if needed.",
            styles,
        )
    )
    story.append(subsection("6.2 Component Diagram Explanation", styles))
    story.append(
        code_block(
            """
+----------------------+         HTTP/JSON          +-----------------------+
|   Next.js Frontend   |  <---------------------->  |   FastAPI Backend     |
|  Ward map, upload UI |                            | Upload, runs, results  |
+----------+-----------+                            +-----------+-----------+
           |                                                        |
           | latest run / upload                                    | orchestrates
           v                                                        v
+----------------------+                            +-----------------------+
| Bundled GeoJSON Data |                            |  Pipeline Orchestrator |
| Ward boundaries      |                            | schema, interpolation  |
+----------------------+                            | feature engineering    |
                                                    +-----------+-----------+
                                                                |
                                                                | loads
                                                                v
                                                    +-----------------------+
                                                    | Model Artifacts       |
                                                    | XGB-like, RF, Torch   |
                                                    +-----------+-----------+
                                                                |
                                                                | stores
                                                                v
                                                    +-----------------------+
                                                    | SQLite + CSV Outputs  |
                                                    | run metadata, exports |
                                                    +-----------------------+
            """,
            styles,
        )
    )
    story.append(subsection("6.3 Data Flow Explanation", styles))
    story.append(
        bullets(
            [
                "A user uploads a rainfall CSV from the dashboard or directly through the API.",
                "The backend stores the upload and creates a run record in SQLite.",
                "The pipeline normalizes columns such as date, lat/lon, and rainfall.",
                "Rainfall is interpolated to the reference model grid using inverse-distance weighting.",
                "Time-series and static geographic features are assembled for each grid coordinate.",
                "An ensemble model computes flood-risk probabilities.",
                "The latest date is extracted and transformed into coordinate-level risk points.",
                "Artifacts are written to CSV and the run summary is saved for retrieval by the frontend.",
            ],
            styles,
        )
    )

    # 7. Technology Stack
    story.append(section("7. Technology Stack", styles))
    story.append(
        table(
            [
                ["Layer", "Technology", "Role in System"],
                ["Frontend", "Next.js 15, React 19, TypeScript, Tailwind CSS, Leaflet", "Dashboard, geospatial visualization, scenario upload UI"],
                ["Backend", "Python 3.11+, FastAPI, Uvicorn", "REST API, orchestration, artifact management"],
                ["Database", "SQLite", "Stores pipeline run metadata and audit trail"],
                ["Data Processing", "Pandas, NumPy", "Schema normalization, interpolation, feature preparation"],
                ["ML Inference", "Custom ensemble + PyTorch", "Risk probability estimation"],
                ["Containerization", "Docker, Docker Compose", "Consistent local and deployment runtime"],
                ["External API", "wttr.in", "Live weather widget fallback for the frontend"],
            ],
            col_widths=[3.2 * cm, 5.6 * cm, 7.4 * cm],
        )
    )

    # 8. Detailed Modules
    story.append(section("8. Detailed Modules", styles))
    story.append(subsection("8.1 Frontend Module", styles))
    story.append(
        p(
            "The frontend is responsible for user interaction, ward visualization, and pipeline upload workflows. "
            "The main page dynamically loads the map and panel components to avoid unnecessary server-side rendering "
            "for browser-specific libraries like Leaflet. It uses a `useFloodData` hook to manage weather sync, latest "
            "run fetch, and scenario submission. When a successful pipeline result is available, the frontend converts "
            "backend result points into map hotspots.",
            styles,
        )
    )
    story.append(subsection("8.2 Backend Module", styles))
    story.append(
        p(
            "The backend provides health endpoints, run listing, latest run retrieval, run download, and scenario upload. "
            "Route handlers remain thin and delegate processing to the pipeline module. This keeps I/O, validation, and "
            "business logic clearly separated. The backend also initializes the SQLite schema on startup so the service is "
            "self-bootstrapping for local development.",
            styles,
        )
    )
    story.append(subsection("8.3 Database Module", styles))
    story.append(
        p(
            "The database layer uses SQLite for simplicity and portability. A single `pipeline_runs` table stores run IDs, "
            "scenario names, input/output paths, timestamps, row counts, summary JSON, and error messages. This supports "
            "auditability and makes the latest successful result query straightforward.",
            styles,
        )
    )
    story.append(subsection("8.4 AI / ML Module", styles))
    story.append(
        p(
            "The machine learning module is an ensemble consisting of a gradient-boosted stump model, a random stump forest, "
            "and a PyTorch multilayer perceptron. The ensemble computes per-coordinate risk and combines model outputs with "
            "fixed normalized weights. This hybrid approach balances interpretability, low runtime overhead, and predictive diversity.",
            styles,
        )
    )

    # 9. Database Design
    story.append(section("9. Database Design", styles))
    story.append(subsection("9.1 Schema Design", styles))
    story.append(
        p(
            "The persistent relational design is intentionally compact because this project stores processing history rather than "
            "transaction-heavy user data. Metadata is normalized enough for reporting, while the large numerical artifacts remain "
            "in CSV files inside the outputs directory.",
            styles,
        )
    )
    story.append(
        table(
            [
                ["Column", "Type", "Purpose"],
                ["run_id", "TEXT PRIMARY KEY", "Unique identifier for a pipeline execution"],
                ["scenario_name", "TEXT", "Human-readable scenario label"],
                ["uploaded_filename", "TEXT", "Original CSV name"],
                ["status", "TEXT", "processing / completed / failed"],
                ["created_at", "TEXT", "Run creation timestamp"],
                ["updated_at", "TEXT", "Last update timestamp"],
                ["input_rows", "INTEGER", "Rows accepted after schema standardization"],
                ["interpolated_rows", "INTEGER", "Rows after grid interpolation"],
                ["output_rows", "INTEGER", "Rows in final risk output"],
                ["latest_prediction_date", "TEXT", "Latest scenario date included in final output"],
                ["upload_path", "TEXT", "Saved original input file"],
                ["interpolated_path", "TEXT", "Intermediate interpolated CSV"],
                ["enriched_path", "TEXT", "Feature-enriched CSV"],
                ["predictions_path", "TEXT", "Full prediction CSV"],
                ["final_output_path", "TEXT", "Coordinate risk CSV for consumers"],
                ["summary_json", "TEXT", "Serialized summary payload"],
                ["error_message", "TEXT", "Failure details when processing fails"],
            ],
            col_widths=[4.2 * cm, 3.2 * cm, 9.0 * cm],
        )
    )
    story.append(subsection("9.2 Relationships", styles))
    story.append(
        bullets(
            [
                "One pipeline run owns many generated artifact files, but those files are stored on disk rather than as child rows.",
                "The backend treats `run_id` as the primary key for both database lookup and artifact-folder naming.",
                "The frontend consumes run summaries and result points through API responses instead of querying the database directly.",
            ],
            styles,
        )
    )

    # 10. API Design
    story.append(section("10. API Design", styles))
    story.append(
        table(
            [
                ["Method", "Endpoint", "Purpose"],
                ["GET", "/", "Service metadata and quick links"],
                ["GET", "/health", "Health-check endpoint"],
                ["GET", "/api/pipeline/runs", "List recent pipeline runs"],
                ["GET", "/api/pipeline/runs/latest", "Get latest successful run"],
                ["GET", "/api/pipeline/runs/{run_id}", "Get run details"],
                ["GET", "/api/pipeline/runs/{run_id}/download", "Download final result CSV"],
                ["POST", "/api/pipeline/runs", "Upload scenario CSV and execute pipeline"],
            ],
            col_widths=[2.0 * cm, 6.0 * cm, 8.4 * cm],
        )
    )
    story.append(subsection("10.1 Example Upload Request", styles))
    story.append(
        code_block(
            """
POST /api/pipeline/runs
Content-Type: multipart/form-data

form-data:
  file = sample_week_flood_rainfall.csv
  scenario_name = monsoon-simulation-week-1
            """,
            styles,
        )
    )
    story.append(subsection("10.2 Example Success Response", styles))
    story.append(
        code_block(
            """
{
  "run": {
    "run_id": "8d3d5f74-2f27-4687-9dc8-1adf1ac9d521",
    "scenario_name": "monsoon-simulation-week-1",
    "status": "completed",
    "input_rows": 840,
    "interpolated_rows": 17500,
    "output_rows": 2500,
    "latest_prediction_date": "2026-07-14",
    "download_url": "/api/pipeline/runs/8d3d5f74-2f27-4687-9dc8-1adf1ac9d521/download",
    "summary": {
      "max_risk": 0.913,
      "mean_risk": 0.274,
      "high_risk_points": 124,
      "medium_risk_points": 418,
      "low_risk_points": 1958
    },
    "result_points": [
      {"lat": 28.7041, "lon": 77.1025, "risk": 0.9131}
    ]
  }
}
            """,
            styles,
        )
    )

    # 11. Workflow / Pipeline
    story.append(section("11. Workflow / Pipeline", styles))
    story.append(
        bullets(
            [
                "Step 1: The client uploads a CSV file through the dashboard or API.",
                "Step 2: The backend validates the file extension and generates a unique run ID.",
                "Step 3: The original file is written into `outputs/pipeline/uploads`.",
                "Step 4: The schema is standardized to canonical names such as `grid_latitude`, `grid_longitude`, and `precipitation_mm`.",
                "Step 5: For each date, rainfall is interpolated over the reference grid using inverse-distance weighting.",
                "Step 6: Rolling and lag features are generated for temporal context.",
                "Step 7: Static spatial features are merged from coordinate-level reference data.",
                "Step 8: The ensemble generates prediction probabilities and binary risk labels.",
                "Step 9: The latest scenario date is transformed into a coordinate risk CSV suitable for visualization.",
                "Step 10: Summary metrics and artifact paths are persisted, and the frontend consumes the result.",
            ],
            styles,
        )
    )

    # 12. Implementation Details
    story.append(section("12. Implementation Details", styles))
    story.append(subsection("12.1 Key Algorithm: Schema Standardization", styles))
    story.append(
        code_block(
            """
def standardize_columns(df):
    rename_map = {}
    if "lat" in df.columns:
        rename_map["lat"] = "grid_latitude"
    if "lon" in df.columns:
        rename_map["lon"] = "grid_longitude"
    if "rainfall" in df.columns:
        rename_map["rainfall"] = "precipitation_mm"

    df = df.rename(columns=rename_map).copy()
    required = {"date", "grid_latitude", "grid_longitude", "precipitation_mm"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df
            """,
            styles,
        )
    )
    story.append(subsection("12.2 Key Algorithm: Grid Interpolation", styles))
    story.append(
        p(
            "The interpolation routine computes weighted rainfall values for a target reference grid. "
            "Observed coordinates for each date are compared against the target grid, exact coordinate matches "
            "are copied directly, and non-exact locations are estimated through inverse-distance weighting. "
            "This makes the platform robust to sparse or irregular input coverage.",
            styles,
        )
    )
    story.append(
        code_block(
            """
distances = np.sqrt(((target_coords[:, None, :] - observed_coords[None, :, :]) ** 2).sum(axis=2))
safe_dist = np.clip(distances[remaining], 1e-6, None)
inverse = 1.0 / np.square(safe_dist)
weights = inverse / inverse.sum(axis=1, keepdims=True)
weighted[remaining] = weights @ observed_rain
            """,
            styles,
        )
    )
    story.append(subsection("12.3 Key Algorithm: Ensemble Prediction", styles))
    story.append(
        code_block(
            """
p_xgb = bundle["xgb_like"].predict_proba(X_raw)[:, 1]
p_rf = bundle["random_forest"].predict_proba(X_raw)[:, 1]
with torch.no_grad():
    logits = bundle["neural_net"](torch.tensor(X_scaled, dtype=torch.float32)).numpy()
p_nn = sigmoid(logits)

raw_weights = np.array([0.6, 0.3, 0.2], dtype=float)
weights = raw_weights / raw_weights.sum()
p_ensemble = weights[0] * p_xgb + weights[1] * p_rf + weights[2] * p_nn
            """,
            styles,
        )
    )

    # 13. UI/UX
    story.append(section("13. UI / UX Description", styles))
    story.append(
        bullets(
            [
                "Top Bar: shows city readiness score and simulation state.",
                "Ward Search: allows quick focus on a specific ward from the map.",
                "Flood Map: renders ward polygons and hotspot overlays with interactive drill-down.",
                "Sidebar: displays weather, pipeline upload form, summary cards, and scenario controls.",
                "Hotspot Panel: reveals detailed information when a ward is selected.",
                "Scenario Upload Card: lets the user upload rainfall CSV files and immediately run prediction.",
            ],
            styles,
        )
    )
    story.append(
        p(
            "The interface design prioritizes operational readability. Color, typography, and layout are chosen to highlight "
            "risk levels and guide attention toward actionable information. The dashboard is designed for analysts and civic "
            "operators, not just developers, so important actions such as uploading a scenario or downloading a result are "
            "placed directly in the main control panel.",
            styles,
        )
    )

    # 14. Deployment
    story.append(section("14. Deployment", styles))
    story.append(
        p(
            "The project supports both direct local execution and containerized deployment. The backend Docker image installs "
            "Python dependencies, copies the API, source code, and required processed model/reference assets, and serves the "
            "application with Uvicorn on port 8000. The frontend Docker image uses a multi-stage Node build and serves the "
            "compiled Next.js application on port 9002. Docker Compose orchestrates the two containers and mounts a named volume "
            "for backend outputs so generated artifacts survive container restarts.",
            styles,
        )
    )
    story.append(
        code_block(
            """
# Local
uvicorn api.app:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev

# Containerized
docker compose up --build
            """,
            styles,
        )
    )

    # 15. Testing
    story.append(section("15. Testing", styles))
    story.append(subsection("15.1 Unit Testing", styles))
    story.append(
        bullets(
            [
                "Validate schema normalization with valid and invalid CSV column combinations.",
                "Test helper functions such as slug creation and summary aggregation.",
                "Verify database CRUD operations for run creation and status updates.",
                "Check feature engineering outputs such as lag and rolling-sum columns.",
            ],
            styles,
        )
    )
    story.append(subsection("15.2 Integration Testing", styles))
    story.append(
        bullets(
            [
                "Upload a sample scenario through the API and verify the generated run metadata.",
                "Confirm that latest-run retrieval returns the newest successful run.",
                "Validate result download and CSV existence checks.",
                "Exercise the frontend flow from upload to hotspot rendering using mock or local API responses.",
            ],
            styles,
        )
    )

    # 16. Security
    story.append(section("16. Security Considerations", styles))
    story.append(
        bullets(
            [
                "Input validation ensures the upload endpoint only accepts CSV files.",
                "The backend does not execute uploaded content; files are treated as data only.",
                "CORS is restricted to expected local frontend origins in the current implementation.",
                "Artifact paths are generated server-side to prevent path traversal by user input.",
                "Sensitive secrets are minimal in the current local architecture; environment files should still be excluded from Git.",
            ],
            styles,
        )
    )
    story.append(
        p(
            "For a production-grade deployment, the next step would be to introduce authentication, signed upload/download access, "
            "request rate limiting, audit logging, and storage hardening for generated artifacts.",
            styles,
        )
    )

    # 17. Scalability
    story.append(section("17. Scalability & Performance", styles))
    story.append(
        bullets(
            [
                "The modular monolith can later be split into dedicated upload, inference, and reporting services.",
                "Model artifacts are cached in memory using `lru_cache`, reducing repeated disk loads.",
                "Static frontend geo-data is bundled locally, reducing backend dependency for initial rendering.",
                "Outputs are written as files rather than bloating the database with large blobs.",
                "A future production version could replace SQLite with PostgreSQL and use object storage for artifacts.",
            ],
            styles,
        )
    )
    story.append(
        p(
            "The current implementation is appropriate for demonstrations, academic submission, local analysis, and moderate internal use. "
            "For higher concurrency or wider public deployment, queue-based asynchronous processing and distributed storage would be advisable.",
            styles,
        )
    )

    # 18. Challenges
    story.append(section("18. Challenges & Solutions", styles))
    story.append(
        table(
            [
                ["Challenge", "Impact", "Solution"],
                ["Irregular rainfall input schemas", "Pipelines fail on inconsistent column names", "Added standardization logic that accepts multiple aliases"],
                ["Sparse coordinate coverage", "Missing prediction coverage over the city grid", "Applied inverse-distance interpolation to a fixed reference grid"],
                ["Frontend/backend integration", "Visualization may show stale or incompatible data", "Defined a stable latest-run API contract with summary and points"],
                ["Large local data footprint", "Repository becomes too large for GitHub", "Ignored raw data and kept only lightweight runtime artifacts in version control"],
                ["Model compatibility across saved artifacts", "Legacy pickled classes may fail to load", "Implemented a legacy unpickler map for backward compatibility"],
            ],
            col_widths=[4.0 * cm, 5.0 * cm, 7.4 * cm],
        )
    )

    # 19. Future Scope
    story.append(section("19. Future Scope", styles))
    story.append(
        bullets(
            [
                "Add authenticated multi-user support for municipal departments or agencies.",
                "Replace mock ward-risk fallbacks with full backend-driven geospatial summaries.",
                "Integrate historical flood events and live sensor feeds for better calibration.",
                "Introduce asynchronous job processing with Celery, Redis, or a cloud queue.",
                "Add explainable-AI summaries showing which features most influenced local risk predictions.",
                "Deploy on a managed cloud stack with PostgreSQL, object storage, and monitoring dashboards.",
            ],
            styles,
        )
    )

    # 20. Conclusion
    story.append(section("20. Conclusion", styles))
    story.append(
        p(
            "The Delhi Flood Intelligence Platform is a strong end-to-end engineering project because it connects real data-handling concerns "
            "with practical product delivery. The system demonstrates backend API design, geospatial processing, ML inference, persistence, "
            "frontend visualization, and deployment readiness in one coherent workflow. It is suitable for viva examinations, interviews, and "
            "project submission because each major software engineering concern can be discussed clearly: problem definition, architecture, "
            "module design, API contracts, data modeling, security, testing, and future extensibility.",
            styles,
        )
    )

    story.append(Spacer(1, 0.4 * cm))
    story.append(
        p(
            "End of document.",
            styles,
            "SmallMuted",
        )
    )
    return story


def generate_pdf(output_path: Path) -> None:
    """Build the PDF report."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=2.1 * cm,
        bottomMargin=1.8 * cm,
        title=PROJECT_NAME,
        author=AUTHOR,
        subject="Comprehensive software project documentation",
    )
    story = build_story()
    doc.build(story, onFirstPage=page_header_footer, onLaterPages=page_header_footer)


if __name__ == "__main__":
    generate_pdf(OUTPUT_FILE)
    print(f"PDF generated successfully: {OUTPUT_FILE.resolve()}")
