from pathlib import Path

import pytest

from readme_weaver.include_content_reader import IncludeContentReader
from readme_weaver.include_metadata_extractor import IncludeMetadataExtractor
from readme_weaver.readme_weaver import ReadmeWeaver


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_include_replaces_content(tmp_path: Path, monkeypatch) -> None:
    """Ensure that include directives are replaced with file content."""
    partial_dir = tmp_path / "partials"
    partial_file = partial_dir / "hello.md"
    write_file(partial_file, "# Hello\nWorld")

    readme = tmp_path / "README.md"
    readme_content = """Intro\n<!-- md:include start path=\"partials/hello.md\" required=true -->\nplaceholder\n<!-- md:include end -->\nOutro\n"""
    write_file(readme, readme_content)

    monkeypatch.setenv("README_WEAVER_BASE", str(tmp_path))

    extractor = IncludeMetadataExtractor()
    reader = IncludeContentReader()
    weaver = ReadmeWeaver(
        readme_paths=[str(readme)],
        changed_files=None,
        include_metadata_extractor=extractor,
        include_content_reader=reader,
    )
    weaver()

    updated = read_file(readme)

    assert "placeholder" not in updated
    assert "Hello" in updated
    assert "World" in updated


def test_missing_required_raises(tmp_path: Path, monkeypatch) -> None:
    """A missing required include should raise FileNotFoundError."""
    readme = tmp_path / "README.md"
    content = (
        'Intro\n<!-- md:include start path="missing.md" -->\ntext\n<!-- md:include end -->\n'
    )
    write_file(readme, content)
    monkeypatch.setenv("README_WEAVER_BASE", str(tmp_path))
    extractor = IncludeMetadataExtractor()
    reader = IncludeContentReader()
    weaver = ReadmeWeaver(
        readme_paths=[str(readme)],
        changed_files=None,
        include_metadata_extractor=extractor,
        include_content_reader=reader,
    )
    with pytest.raises(FileNotFoundError):
        weaver()


def test_missing_not_required_is_empty(tmp_path: Path, monkeypatch) -> None:
    """A missing non-required include should result in an empty block."""
    readme = tmp_path / "README.md"
    content = """Header\n<!-- md:include start path=\"missing.md\" required=false -->\nplaceholder\n<!-- md:include end -->\nFooter"""
    write_file(readme, content)
    monkeypatch.setenv("README_WEAVER_BASE", str(tmp_path))
    extractor = IncludeMetadataExtractor()
    reader = IncludeContentReader()
    weaver = ReadmeWeaver(
        readme_paths=[str(readme)],
        changed_files=None,
        include_metadata_extractor=extractor,
        include_content_reader=reader,
    )
    weaver()
    updated = read_file(readme)

    assert "placeholder" not in updated

    lines = updated.splitlines()
    start_idx = [i for i, l in enumerate(lines) if l.startswith("<!-- md:include start")][0]
    end_idx = [i for i, l in enumerate(lines) if l.startswith("<!-- md:include end")][0]

    assert end_idx == start_idx + 2


def test_base_dir_env_var(tmp_path: Path, monkeypatch) -> None:
    """Include paths are resolved relative to README_WEAVER_BASE environment variable."""
    base_dir = tmp_path / "base"
    partials = base_dir / "partials"
    hello = partials / "hello.md"
    write_file(hello, "Hello env")
    readme = tmp_path / "README.md"
    content = 'Header\n<!-- md:include start path="partials/hello.md" -->\nX\n<!-- md:include end -->\n'
    write_file(readme, content)
    monkeypatch.setenv("README_WEAVER_BASE", str(base_dir))
    extractor = IncludeMetadataExtractor()
    reader = IncludeContentReader()
    weaver = ReadmeWeaver(
        readme_paths=[str(readme)],
        changed_files=None,
        include_metadata_extractor=extractor,
        include_content_reader=reader,
    )
    weaver()
    updated = read_file(readme)
    assert "Hello env" in updated
