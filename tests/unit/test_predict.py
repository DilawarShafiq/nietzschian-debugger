"""Tests for predict mode. The LLM dare/verdict needs a key, but the part that
matters most — execution as ground truth — is tested here with no key."""

from __future__ import annotations

import pytest

from nietzschian_debugger.commands import predict


@pytest.fixture
def sandbox_available():
    syspath, _ = predict._module_spec("nietzschian_debugger/core/lens_state.py")
    command, error = predict._sandbox_command(syspath)
    if command is None:
        pytest.skip(error)
    out = predict._run_subprocess('print(\'{"stage":"ready"}\')', {"syspath": syspath})
    assert out and out.get("stage") == "ready", out


def test_prompts_are_in_voice_and_withhold_the_answer() -> None:
    assert "PREDICT mode" in predict.DARE_SYSTEM
    assert "PREDICT mode" in predict.JUDGE_SYSTEM
    assert "never reveal" in predict.DARE_SYSTEM.lower()
    # The judge must trust the executed result, not its own reasoning.
    assert "truth" in predict.JUDGE_SYSTEM.lower()


def test_empty_file_exits_before_any_api_call(tmp_path) -> None:
    f = tmp_path / "empty.py"
    f.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit):
        predict.predict_command(str(f))


def test_missing_file_exits(tmp_path) -> None:
    with pytest.raises(SystemExit):
        predict.predict_command(str(tmp_path / "does_not_exist.py"))


def test_module_spec_for_package_file() -> None:
    _syspath, module = predict._module_spec("nietzschian_debugger/core/lens_state.py")
    assert module == "nietzschian_debugger.core.lens_state"


def test_parse_dare_extracts_call_and_cleans_the_dare() -> None:
    text = 'DARE: You think you know it? what does f(0) return?\nCALL: {"function": "f", "args": [0]}'
    dare, call = predict._parse_dare(text)
    assert call == {"function": "f", "args": [0]}
    assert "what does f(0) return" in dare
    assert "CALL" not in dare and "DARE:" not in dare


def test_execution_is_ground_truth(sandbox_available) -> None:
    # This is the whole point: the reasoning-only prototype said the answer was
    # ('avoiding', ' ') — a space. RUNNING the code gives the real answer. No model,
    # no guessing, no fooling yourself.
    syspath, module = predict._module_spec("nietzschian_debugger/core/lens_state.py")
    out = predict.execute_call(syspath, module, "parse_state_tag", ["[STATE: AVOIDING] "])
    assert out["stage"] == "ran"
    assert out["returned"] == "('avoiding', '')"


def test_guard_rejects_methods_and_accepts_functions(sandbox_available) -> None:
    # The 7B dared with `observe` — a METHOD of LensTracker, not runnable alone.
    # The guard must reject it and accept a real top-level function.
    syspath, module = predict._module_spec("nietzschian_debugger/core/lens_state.py")
    assert predict.is_callable_top_level(syspath, module, "parse_state_tag") is True
    assert predict.is_callable_top_level(syspath, module, "observe") is False


def test_parse_dare_strips_label_even_after_a_preamble() -> None:
    # Regression: the 7B wrote a gleeful line BEFORE "DARE:", so the label wasn't
    # leading and leaked into the question.
    text = 'I bet you a golden coin!\n\nDARE: what does f() return?\nCALL: {"function": "f", "args": []}'
    dare, call = predict._parse_dare(text)
    assert call == {"function": "f", "args": []}
    assert "DARE:" not in dare
    assert "golden coin" in dare and "what does f() return" in dare


def test_parse_match_tag() -> None:
    correct, verdict = predict._parse_match("MATCH: no\n\nWrong — you skipped the early return.")
    assert correct is False
    assert verdict.startswith("Wrong")
    correct, _ = predict._parse_match("MATCH: yes\nRight, and it was easy.")
    assert correct is True
    correct, text = predict._parse_match("no tag at all?")
    assert correct is None and text == "no tag at all?"


def test_execution_captures_a_raise(sandbox_available) -> None:
    # A function that raises is a legitimate "behaviour" — captured, not crashed.
    syspath, module = predict._module_spec("nietzschian_debugger/llm/validator.py")
    out = predict.execute_call(syspath, module, "get_fallback_question", ["not-a-real-intensity"])
    assert out["stage"] == "ran"
    assert "raised" in out  # KeyError on the unknown intensity


def test_unsupported_platform_never_starts_python(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(predict.platform, "system", lambda: "Darwin")

    def unexpected_run(*args, **kwargs):
        pytest.fail("Unsupported platform must not execute code")

    monkeypatch.setattr(predict.subprocess, "run", unexpected_run)
    out = predict.execute_call(str(tmp_path), "malicious", "f", [])
    assert out["stage"] == "setup"
    assert "disabled" in out["error"]
    assert not predict.is_callable_top_level(str(tmp_path), "malicious", "f")


def test_missing_bubblewrap_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(predict.platform, "system", lambda: "Linux")
    monkeypatch.setattr(predict.shutil, "which", lambda _: None)
    out = predict.execute_call(str(tmp_path), "anything", "f", [])
    assert out["stage"] == "setup"
    assert "bubblewrap" in out["error"]


def test_preflight_fails_before_api_access(monkeypatch, tmp_path) -> None:
    f = tmp_path / "example.py"
    f.write_text("def f(): return 1", encoding="utf-8")
    monkeypatch.setattr(predict.platform, "system", lambda: "Windows")

    def unexpected_api():
        pytest.fail("Sandbox preflight must happen before any API access")

    monkeypatch.setattr(predict, "get_client", unexpected_api)
    with pytest.raises(SystemExit) as error:
        predict.predict_command(str(f))
    assert error.value.code == 2


def test_failed_sandbox_does_not_retry_unsandboxed(monkeypatch, tmp_path) -> None:
    from subprocess import CompletedProcess

    calls = []
    monkeypatch.setattr(predict, "_sandbox_command", lambda _: (["bwrap"], None))

    def denied(command, **kwargs):
        calls.append(command)
        assert command[0] == "bwrap"
        assert '"syspath": "/workspace"' in kwargs["input"]
        return CompletedProcess(command, 1, "", "namespace creation denied")

    monkeypatch.setattr(predict.subprocess, "run", denied)
    out = predict.execute_call(str(tmp_path), "example", "f", [])
    assert out == {"stage": "setup", "error": "namespace creation denied"}
    assert len(calls) == 1


def test_sandbox_blocks_import_time_host_write(tmp_path, sandbox_available) -> None:
    project = tmp_path / "project"
    project.mkdir()
    marker = tmp_path / "host-marker"
    (project / "untrusted.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('bad')\ndef f(): return 1\n",
        encoding="utf-8",
    )
    out = predict.execute_call(str(project), "untrusted", "f", [])
    assert out["stage"] == "setup"
    assert not marker.exists()
    assert not predict.is_callable_top_level(str(project), "untrusted", "f")
    assert not marker.exists()


def test_sandbox_isolates_environment_and_host_files(tmp_path, monkeypatch, sandbox_available) -> None:
    project = tmp_path / "project"
    project.mkdir()
    secret = tmp_path / "private.txt"
    secret.write_text("host-only", encoding="utf-8")
    monkeypatch.setenv("SANDBOX_TEST_SECRET", "environment-only")
    (project / "sample.py").write_text(
        "import os\nfrom pathlib import Path\n"
        "def environment(): return os.environ.get('SANDBOX_TEST_SECRET')\n"
        "def read(path): return Path(path).read_text()\n"
        "def write(): return Path('modified.txt').write_text('bad')\n",
        encoding="utf-8",
    )
    out = predict.execute_call(str(project), "sample", "environment", [])
    assert out == {"stage": "ran", "returned": "None"}
    out = predict.execute_call(str(project), "sample", "read", [str(secret)])
    assert "raised" in out
    out = predict.execute_call(str(project), "sample", "write", [])
    assert "raised" in out
    assert not (project / "modified.txt").exists()


def test_sandbox_has_no_network(tmp_path, sandbox_available) -> None:
    import socket

    project = tmp_path / "project"
    project.mkdir()
    (project / "sample.py").write_text(
        "import socket\n"
        "def connect(port):\n"
        "    with socket.create_connection(('127.0.0.1', port), timeout=1):\n"
        "        return 'connected'\n",
        encoding="utf-8",
    )
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        out = predict.execute_call(str(project), "sample", "connect", [server.getsockname()[1]])
    assert "raised" in out
