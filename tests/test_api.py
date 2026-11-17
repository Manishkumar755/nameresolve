import os

import pytest
from fastapi.testclient import TestClient

from nameresolve import train

KEY = "test-key"


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    model_path = tmp_path_factory.mktemp("models") / "model.joblib"
    train.main(n_entities=60, out=model_path)
    os.environ["MODEL_PATH"] = str(model_path)
    os.environ["API_KEY"] = KEY
    from nameresolve.api import app

    with TestClient(app) as c:
        yield c


def test_rejects_missing_key(client):
    r = client.post("/v1/match", json={"query": "a", "candidates": ["b"]})
    assert r.status_code == 401


def test_returns_ranked_matches(client):
    r = client.post(
        "/v1/match",
        headers={"X-API-Key": KEY},
        json={"query": "Shreya Verma", "candidates": ["Sreya Verma", "Rahul Gupta"], "top_k": 2},
    )
    assert r.status_code == 200
    scores = [m["score"] for m in r.json()["matches"]]
    assert scores == sorted(scores, reverse=True)