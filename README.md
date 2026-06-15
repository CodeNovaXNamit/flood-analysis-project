# Flood Analysis Project"

Flood-risk analysis workspace for Delhi with:

- a FastAPI backend that accepts rainfall CSV uploads and returns coordinate-level flood-risk predictions
- a Next.js frontend dashboard for ward visualization, hotspot inspection, and scenario uploads
- a Gemini-powered flood response copilot that converts structured flood telemetry into operational recommendations
- Python data preparation and model code under `src/`

## Repository Layout:

- `api/` FastAPI app, upload endpoints, pipeline orchestration, and local SQLite run history
- `frontend/` Next.js dashboard UI
- `src/` reusable Python modules for loading data, geospatial work, feature engineering, training, and inference
- `scripts/` CLI wrappers and utility scripts
- `configs/` project configuration files
- `docs/` architecture and methodology notes
- `tests/` Python tests
- `generate_project_documentation_pdf.py` PDF generator for the complete project report
- `generate_gemini_integration_documentation_pdf.py` PDF generator for the Gemini integration strategy report
- `data/processed/models/` small model artifacts required by the API at runtime
- `data/processed/references/` reference grid files and example input template
- `outputs/` generated pipeline runs and local SQLite database files

## Gemini Integration:

The frontend now includes a `Gemini Flood Copilot` powered by Genkit and the Google GenAI plugin.

It uses real structured project data to generate:

- escalation level
- ranked municipal actions
- ward-level focus recommendations
- short flood-risk projection
- public advisory text

The AI layer does not replace the flood prediction pipeline. It interprets the project’s deterministic and ML outputs for operators and judges.

### Gemini Setup:

Set one of these variables in `frontend/.env`:

```bash
GEMINI_API_KEY=your_key_here
# or
GOOGLE_API_KEY=your_key_here
# or
GOOGLE_GENAI_API_KEY=your_key_here
```

If no Google AI key is present, the copilot falls back to a local deterministic advisory path so the UI still remains functional.

For local frontend setup, you can copy `frontend/.env.example` into `frontend/.env` and fill in the values you want to use.

## What The Backend Expects

The upload API expects a rainfall CSV with these columns:

- `date`
- `lat` or `grid_latitude`
- `lon` or `grid_longitude`
- `rainfall` or `precipitation_mm`

Useful examples already in the repo:

- `data/processed/references/test_input_template.csv`
- `data/processed/scenarios/sample_new_data.csv`
- `data/processed/scenarios/sample_week_flood_rainfall.csv`

## Local Run

### 1. Backend

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the API from the repo root:

```bash
uvicorn api.app:app --host 127.0.0.1 --port 8000
```

Useful endpoints:

- `GET /`
- `GET /health`
- `GET /docs`
- `GET /api/pipeline/runs/latest`
- `POST /api/pipeline/runs`

### 2. Frontend

Install dependencies:

```bash
cd frontend
npm install
```

Start the Next.js app:

```bash
npm run dev
```

Open `http://localhost:9002`.

If you want the frontend to call a non-default backend URL, set:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

If you want live Gemini-backed recommendations in the copilot dialog, also add one of the Gemini API keys shown above to `frontend/.env`.

### 2A. Frontend On Vercel

Deploy the `frontend/` app as a separate Vercel project with:

- Framework Preset: `Next.js`
- Root Directory: `frontend`
- Build Command: `next build`
- Output Directory: leave empty
- Install Command: `npm install`

Set these Vercel environment variables for the frontend project:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain
GEMINI_API_KEY=your_key_here
```

The frontend should not be deployed with the `FastAPI` preset because the repo root is a monorepo, not a single Python app.

### 2B. Backend On A Python Host

Deploy the `api/` service separately on a Python-friendly host such as Render, Railway, Fly.io, or Google Cloud Run.

Typical backend start command:

```bash
uvicorn api.app:app --host 0.0.0.0 --port $PORT
```

Set backend CORS so the Vercel frontend can call it:

```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

You can provide multiple origins as a comma-separated list:

```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-custom-domain.com
```

### 3. Docker Option

You can also run the backend and frontend with Docker:

```bash
docker compose up --build
```

Backend: `http://localhost:8000`

Frontend: `http://localhost:9002`

## GitHub Upload Notes

This repo has been prepared to keep Git history smaller and cleaner:

- raw data, interim data, outputs, archives, and local build artifacts are ignored
- only the lightweight runtime assets required by the API are allowed from `data/processed/models` and `data/processed/references`
- frontend `node_modules` and `.next` output are ignored

Before pushing, review `git status` and decide whether you want to keep any currently untracked local-only files.

If a real API key was ever committed into a tracked `.env` file, rotate that key before publishing or redeploying.

For a public or lightweight repo, keep these out of Git:

- large raw datasets
- generated predictions and pipeline outputs
- local archives such as `.zip` or `.rar`

If you need to version large datasets later, use Git LFS instead of normal Git objects.

## Current Caveats

- The API will not run from a fresh clone unless the required files under `data/processed/models` and `data/processed/references` are present.
- Weather in the frontend is fetched from `https://wttr.in/Delhi?format=j1`; if that request fails, the UI falls back to bundled mock values.
- The frontend is still wired to bundled ward and hotspot data unless a successful pipeline run is available.

## Testing

Run Python tests from the repo root:

```bash
pytest
```

Run the frontend type check:

```bash
cd frontend
npm run typecheck
```

## Documentation PDFs

Generate the full project documentation PDF:

```bash
python generate_project_documentation_pdf.py
```

Generate the Gemini integration strategy PDF:

```bash
python generate_gemini_integration_documentation_pdf.py
```

Generated outputs:

- `Flood_Analysis_Project_Documentation.pdf`
- `Gemini_Integration_Strategy_Flood_Analysis_Project.pdf`
