from nameresolve.features import FEATURE_NAMES, pair_features


def _f(x, y):
    return dict(zip(FEATURE_NAMES, pair_features(x, y)))


def test_identical_names_are_maximal():
    f = _f("Shreya Verma", "Shreya Verma")
    assert f["jaro_winkler"] == 1.0


def test_reorder_detected():
    f = _f("Singh Harpreet", "Harpreet Singh")
    assert f["same_tokens"] == 1.0