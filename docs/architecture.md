# Architecture

## Intended structure

- `src/data_loading/`: dataset ingestion, merges, and preprocessing.
- `src/data_loading/flood_modeling/`: flood-modeling specific dataset assembly scripts.
- `src/geospatial/`: reusable spatial utilities and compatibility entry points.
- `src/geospatial/flood_modeling/`: flood-modeling spatial preparation scripts.
- `src/features/`: feature engineering logic.
- `src/models/`: training, prediction, and evaluation.
- `scripts/`: command-line wrappers for running the pipeline from the repo root.
- `data/raw/`: original source inputs only.
- `data/interim/`: derived staging files, scratch spatial joins, and temporary merged tables.
- `data/processed/`: stable processed datasets.
- `data/external/`: externally sourced sample/reference data.
- `outputs/`: final artifacts such as models, predictions, and frontend exports.

## Current placement decisions

- `src/models/train.py` is the main training module.
- `src/models/predict.py` is the main inference module.
- `src/models/evaluate.py` is the evaluation module, while `src/models/evalute.py` remains as a compatibility alias.
- Flood-modeling data-prep scripts now live in `src/data_loading/flood_modeling/`.
- Flood-modeling geospatial scripts now live in `src/geospatial/flood_modeling/`.
- Exploratory notebooks belong in `notebooks/`, not under `src/`.
- Generated workspace files under the old `data/raw/elevation/` working folders were mirrored into `data/interim/flood_modeling/`.
