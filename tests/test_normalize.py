from nameresolve.normalize import normalize


def test_drops_honorific_and_punctuation():
    assert normalize("Mr. Harpreet  Singh!") == "harpreet singh"


def test_initial_dot_removed():
    assert normalize("H. Singh") == "h singh"