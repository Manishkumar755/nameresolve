"""Train the pair classifier and report results on held-out entities.

Run with:  uv run python -m nameresolve.train
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, precision_recall_curve

from nameresolve.features import FEATURE_NAMES, pair_features
from nameresolve.generator import generate, make_pairs, split_entities, split_pairs

MODEL_VERSION = "0.1.0"
ARTIFACT = Path("artifacts/model.joblib")


def to_xy(pairs):
    X = np.array([pair_features(a.name, b.name) for a, b, _ in pairs])
    y = np.array([label for _, _, label in pairs])
    return X, y


def pick_threshold(y, scores, min_precision: float = 0.95) -> float:
    """Highest-recall threshold whose precision still meets min_precision."""
    precision, recall, thresholds = precision_recall_curve(y, scores)
    ok = np.where(precision[:-1] >= min_precision)[0]
    if len(ok) == 0:
        return 0.5  # fallback; reported so it stays visible
    best = ok[np.argmax(recall[ok])]
    return float(thresholds[best])


def evaluate(y, scores, thr: float) -> dict:
    pred = scores >= thr
    tp = int(np.sum(pred & (y == 1)))
    fp = int(np.sum(pred & (y == 0)))
    fn = int(np.sum(~pred & (y == 1)))
    return {
        "pr_auc": round(float(average_precision_score(y, scores)), 4),
        "threshold": round(float(thr), 4),
        "precision": round(tp / (tp + fp), 4) if tp + fp else 0.0,
        "recall": round(tp / (tp + fn), 4) if tp + fn else 0.0,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def main(n_entities: int = 200, seed: int = 42, out: Path = ARTIFACT) -> dict:
    rng = random.Random(seed)
    records = generate(n_entities=n_entities, seed=seed)
    ents = sorted({r.entity_id for r in records})
    tr_e, va_e, te_e = split_entities(ents, rng)
    splits = split_pairs(make_pairs(records, rng), tr_e, va_e, te_e)

    Xtr, ytr = to_xy(splits["train"])
    Xva, yva = to_xy(splits["val"])
    Xte, yte = to_xy(splits["test"])

    jw = FEATURE_NAMES.index("jaro_winkler")

    # Baseline: Jaro-Winkler alone, threshold tuned on validation.
    baseline_thr = pick_threshold(yva, Xva[:, jw])
    baseline = evaluate(yte, Xte[:, jw], baseline_thr)

    # Model: gradient boosting with probability calibration.
    base = HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.05, class_weight="balanced", random_state=seed
    )
    model = CalibratedClassifierCV(base, method="isotonic", cv=3)
    model.fit(Xtr, ytr)

    thr = pick_threshold(yva, model.predict_proba(Xva)[:, 1])
    model_report = evaluate(yte, model.predict_proba(Xte)[:, 1], thr)

    report = {
        "entities": {"train": len(tr_e), "val": len(va_e), "test": len(te_e)},
        "pairs": {"train": len(ytr), "val": len(yva), "test": len(yte)},
        "baseline_jaro_winkler": baseline,
        "gradient_boosting": model_report,
    }
    print(json.dumps(report, indent=2))

    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": model, "threshold": thr, "features": FEATURE_NAMES, "version": MODEL_VERSION},
        out,
    )
    return report


if __name__ == "__main__":
    main()