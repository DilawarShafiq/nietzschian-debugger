"""predict: a model that fumbles the dare gets a firmer second (and third) chance.

The model is a fake that answers from a script, so no key is needed. The guard that
checks the chosen function is real: it runs against core/lens_state.py, where
`parse_state_tag` is a top-level function and `observe` is only a method."""

from __future__ import annotations

import pytest

from nietzschian_debugger.commands import predict

GOOD = 'DARE: You think you know it? what does parse_state_tag("") return?\nCALL: {"function": "parse_state_tag", "args": [""]}'
FILE = "nietzschian_debugger/core/lens_state.py"


class FakeModel:
    """Stands in for call_llm: returns the scripted answers in order, records each ask."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = []

    def __call__(self, system, messages, model):
        self.calls.append({"system": system, "user": messages[-1]["content"]})
        return self.answers.pop(0)


@pytest.fixture
def ask(monkeypatch):
    dims: list[str] = []
    monkeypatch.setattr(predict, "display_dim", dims.append)
    syspath, module = predict._module_spec(FILE)

    def run(*answers, avoid=None):
        fake = FakeModel(*answers)
        monkeypatch.setattr(predict, "call_llm", fake)
        out = predict._ask_dare("def f(): pass", FILE, "m", syspath, module, avoid or [])
        return out, fake, dims

    return run


def test_a_good_first_dare_is_asked_once_with_the_plain_prompt(ask) -> None:
    out, fake, dims = ask(GOOD)
    assert out is not None and out[1] == {"function": "parse_state_tag", "args": [""]}
    assert len(fake.calls) == 1
    # Unchanged for models that get it right: no firm note, no avoid list.
    assert fake.calls[0]["system"] == predict.DARE_SYSTEM
    assert "Do NOT choose" not in fake.calls[0]["user"]
    assert dims == []


@pytest.mark.parametrize(
    "fumble, hint",
    [
        ("", "was empty"),
        ("   \n ", "was empty"),
        ("DARE: a dare in prose, and no call at all.", "no CALL: line"),
        ("DARE: x\nCALL: {function: parse_state_tag, args: [}", "not valid one-line JSON"),
        ('DARE: x\nCALL: {"function": "parse_state_tag", "args": {"text": ""}}', "args as a JSON list"),
        ('DARE: x\nCALL: {"args": [1]}', "not valid one-line JSON"),
        ('CALL: {"function": "parse_state_tag", "args": [""]}', "no DARE:"),
    ],
)
def test_each_failure_shape_gets_a_firmer_retry(ask, fumble, hint) -> None:
    out, fake, dims = ask(fumble, GOOD)
    assert out is not None and out[1]["function"] == "parse_state_tag"
    assert len(fake.calls) == 2
    assert fake.calls[1]["system"].startswith(predict.DARE_SYSTEM)
    assert "broke the rules" in fake.calls[1]["system"] and hint in fake.calls[1]["system"]
    assert "{{" not in fake.calls[1]["system"]
    assert dims == []


def test_a_non_callable_function_is_named_and_avoided(ask) -> None:
    method = 'DARE: x\nCALL: {"function": "observe", "args": []}'
    out, fake, _ = ask(method, GOOD)
    assert out is not None and out[1]["function"] == "parse_state_tag"
    assert "`observe` is not a directly callable" in fake.calls[1]["system"]
    assert "Do NOT choose any of these functions (already used or not callable): observe." in fake.calls[1]["user"]


def test_an_already_used_function_is_refused(ask) -> None:
    out, fake, _ = ask(GOOD, GOOD, GOOD, avoid=["parse_state_tag"])
    assert out is None
    assert len(fake.calls) == predict._DARE_ATTEMPTS
    assert "(already used): parse_state_tag." in fake.calls[0]["user"]
    assert "`parse_state_tag` was already used" in fake.calls[1]["system"]


def test_gives_up_calmly_after_the_last_attempt(ask) -> None:
    out, fake, dims = ask("", "prose only", 'DARE: x\nCALL: {"function": "observe", "args": []}')
    assert out is None
    assert len(fake.calls) == predict._DARE_ATTEMPTS == 3
    assert dims == [predict._GAVE_UP]
    assert "Traceback" not in predict._GAVE_UP and "error" not in predict._GAVE_UP.lower()


def test_a_model_none_answer_is_treated_as_empty(ask) -> None:
    out, fake, _ = ask(None, GOOD)
    assert out is not None
    assert "was empty" in fake.calls[1]["system"]


def test_a_model_error_still_ends_the_round(ask, monkeypatch) -> None:
    errors: list[str] = []
    monkeypatch.setattr(predict, "display_error", errors.append)

    def boom(*_a):
        raise RuntimeError("HTTP 500")

    monkeypatch.setattr(predict, "call_llm", boom)
    syspath, module = predict._module_spec(FILE)
    assert predict._ask_dare("x", FILE, "m", syspath, module, []) is None
    assert errors and "HTTP 500" in errors[0]


def test_run_round_ends_without_asking_for_a_guess_when_no_dare(ask, monkeypatch) -> None:
    def no_input(*_a):
        raise AssertionError("input() must not be called without a dare")

    monkeypatch.setattr("builtins.input", no_input)
    monkeypatch.setattr(predict, "call_llm", FakeModel("", "", ""))
    monkeypatch.setattr(predict, "display_dim", lambda *_a: None)
    syspath, module = predict._module_spec(FILE)
    assert predict._run_round("x", FILE, "m", syspath, module, []) is None
