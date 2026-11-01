"""Reflection stays separate from code reading, execution, and persistence."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from nietzschian_debugger.cli import cli
from nietzschian_debugger.commands import reflect


@pytest.fixture
def configured(monkeypatch):
    from nietzschian_debugger.llm import providers

    monkeypatch.setattr(providers, "active", lambda: object())
    monkeypatch.setattr(reflect, "get_conversation_model", lambda: "test-model")


def test_empty_topic_does_not_access_api(monkeypatch) -> None:
    monkeypatch.setattr(reflect, "get_client", lambda: pytest.fail("Unexpected API access"))
    with pytest.raises(SystemExit) as error:
        reflect.reflect_command(" ")
    assert error.value.code == 2


def test_conversation_preserves_answers_and_skips_blank_input(monkeypatch, configured) -> None:
    calls = []

    def model(system, messages, name):
        calls.append([dict(message) for message in messages])
        return "What does that belief mean to you?"

    answers = iter(["", "A learned expectation.", "quit"])
    monkeypatch.setattr(reflect, "call_llm", model)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    reflect.reflect_command("I postpone decisions.")
    assert len(calls) == 2
    assert calls[1][-1] == {"role": "user", "content": "A learned expectation."}


def test_invalid_output_is_retried(monkeypatch, configured, capsys) -> None:
    responses = iter(["You should change your habit.", "What do you notice before postponing?"])
    monkeypatch.setattr(reflect, "call_llm", lambda *args: next(responses))
    monkeypatch.setattr("builtins.input", lambda _: "quit")
    reflect.reflect_command("I postpone decisions.")
    output = capsys.readouterr().out
    assert "What do you notice before postponing?" in output
    assert "You should change" not in output


def test_provider_error_exits_explicitly(monkeypatch, configured) -> None:
    def unavailable(*args):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(reflect, "call_llm", unavailable)
    with pytest.raises(SystemExit) as error:
        reflect.reflect_command("A personal topic.")
    assert error.value.code == 3


def test_safety_response_can_override_question_only_rule(monkeypatch, configured, capsys) -> None:
    monkeypatch.setattr(
        reflect,
        "call_llm",
        lambda *args: "[SAFETY] Please contact local emergency services or a trusted person now.",
    )
    monkeypatch.setattr("builtins.input", lambda _: "quit")
    reflect.reflect_command("An urgent situation.")
    output = capsys.readouterr().out
    assert "contact local emergency services" in output
    assert "[SAFETY]" not in output


def test_cli_configures_provider_and_passes_topic(monkeypatch) -> None:
    from nietzschian_debugger.llm import providers

    calls = []
    monkeypatch.setattr(providers, "configure", lambda spec: calls.append(spec))
    monkeypatch.setattr(reflect, "reflect_command", lambda topic: calls.append(topic))
    result = CliRunner().invoke(cli, ["reflect", "A personal topic.", "--model", "ollama:llama3"])
    assert result.exit_code == 0
    assert calls == ["ollama:llama3", "A personal topic."]
