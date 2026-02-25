"""Tests for file reader."""

import pytest

from nietzschian_debugger.storage.file_reader import (
    detect_file_paths,
    read_code_file,
    format_code_context,
)


class TestDetectFilePaths:
    def test_detects_relative_path_with_dot_slash(self) -> None:
        paths = detect_file_paths("Look at ./src/auth.ts for the bug")
        assert "./src/auth.ts" in paths

    def test_detects_relative_path_with_dot_slash_prefix(self) -> None:
        paths = detect_file_paths("Check ./src/models/user.ts")
        assert "./src/models/user.ts" in paths

    def test_detects_paths_in_quotes(self) -> None:
        paths = detect_file_paths('The file "./src/index.ts" has the issue')
        assert "./src/index.ts" in paths

    def test_detects_paths_in_backticks(self) -> None:
        paths = detect_file_paths("Look at `./src/utils.ts`")
        assert "./src/utils.ts" in paths

    def test_detects_multiple_paths(self) -> None:
        paths = detect_file_paths("Compare ./src/a.ts and ./src/b.ts")
        assert len(paths) == 2
        assert "./src/a.ts" in paths
        assert "./src/b.ts" in paths

    def test_deduplicates_repeated_paths(self) -> None:
        paths = detect_file_paths("./src/a.ts and again ./src/a.ts")
        assert len(paths) == 1

    def test_ignores_urls(self) -> None:
        paths = detect_file_paths("Visit http://example.com/page.html for docs")
        has_url = any("example.com" in p for p in paths)
        assert has_url is False

    def test_detects_paths_with_various_extensions(self) -> None:
        text = "Files: ./app.js ./style.css ./data.json ./readme.md"
        paths = detect_file_paths(text)
        assert len(paths) >= 4

    def test_returns_empty_for_no_paths(self) -> None:
        paths = detect_file_paths("This is just a normal sentence.")
        assert len(paths) == 0


class TestReadCodeFile:
    @pytest.mark.asyncio
    async def test_reads_real_file_with_numbered_lines(self) -> None:
        content = await read_code_file("./pyproject.toml")
        assert content is not None
        assert "1:" in content
        assert "nietzschian-debugger" in content

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_file(self) -> None:
        content = await read_code_file("./nonexistent-file-xyz.ts")
        assert content is None


class TestFormatCodeContext:
    def test_returns_empty_string_for_no_files(self) -> None:
        result = format_code_context({})
        assert result == ""

    def test_formats_single_file_with_path_header(self) -> None:
        files = {"src/main.ts": '1: console.log("hello")'}
        result = format_code_context(files)
        assert "--- File: src/main.ts ---" in result
        assert "console.log" in result

    def test_formats_multiple_files(self) -> None:
        files = {"src/a.ts": "1: a", "src/b.ts": "1: b"}
        result = format_code_context(files)
        assert "--- File: src/a.ts ---" in result
        assert "--- File: src/b.ts ---" in result
