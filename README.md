# nameresolve

Name-variant entity resolution. Decides whether name spelling variants (Mohammad, Muhammad, Mohd) refer to the same person. Each match comes with explainable features. Served as a FastAPI service.

Status: tested only on a synthetic benchmark. Not verified on real records.

## Results (synthetic test set, 727 pairs)

|Model|Precision|Recall|PR-AUC|
|-|-|-|-|
|Jaro-Winkler baseline|0.981|0.434|0.940|
|Gradient boosting (calibrated)|0.964|0.998|0.999|

## Run locally

Requirement: Python 3.12+ and uv.

uv sync
uv run python -m nameresolve.train
$env:API\_KEY="your-key"
uv run uvicorn nameresolve.api:app --reload

Then open http://127.0.0.1:8000/docs

## Docker

docker build -t nameresolve:0.1.0 .
docker run -p 8000:8000 -e API\_KEY=your-key nameresolve:0.1.0

## Tests

uv run pytest

## Limitations

* Tested only on synthetic data.
* No blocking: all pairs are compared, so it does not scale to millions of records.
* Output is a lead for human review, not an identity decision.

## Privacy

Logs record counts only, never raw names.

\## Live demo: https://nameresolve.onrender.com/docs

