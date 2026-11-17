"""REST service: POST /v1/match ranks candidate names against a query name."""

from __future__ import annotations

import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from nameresolve.features import pair_features

log = logging.getLogger("nameresolve")
_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("Set the API_KEY environment variable before starting.")
    path = Path(os.environ.get("MODEL_PATH", "artifacts/model.joblib"))
    _state["bundle"] = joblib.load(path)
    _state["api_key"] = api_key
    log.info("model loaded version=%s", _state["bundle"]["version"])
    yield
    _state.clear()


app = FastAPI(title="nameresolve", version="0.1.0", lifespan=lifespan)


def require_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = _state.get("api_key", "")
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="invalid API key")


class MatchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    candidates: list[str] = Field(min_length=1, max_length=200)
    top_k: int = Field(default=5, ge=1, le=50)


class Match(BaseModel):
    candidate: str
    score: float
    is_match: bool
    features: dict[str, float]


class MatchResponse(BaseModel):
    model_version: str
    threshold: float
    matches: list[Match]


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok", "model_loaded": "bundle" in _state}


@app.post("/v1/match", response_model=MatchResponse, dependencies=[Depends(require_key)])
def match(req: MatchRequest) -> MatchResponse:
    bundle = _state["bundle"]
    model, thr, names = bundle["model"], bundle["threshold"], bundle["features"]

    X = np.array([pair_features(req.query, c) for c in req.candidates])
    scores = model.predict_proba(X)[:, 1]
    order = np.argsort(-scores)[: req.top_k]

    matches = [
        Match(
            candidate=req.candidates[i],
            score=round(float(scores[i]), 4),
            is_match=bool(scores[i] >= thr),
            features={n: round(float(v), 4) for n, v in zip(names, X[i])},
        )
        for i in order
    ]
    # Log counts only, never raw names (privacy requirement).
    log.info("match candidates=%d top_k=%d", len(req.candidates), req.top_k)
    return MatchResponse(model_version=bundle["version"], threshold=thr, matches=matches)