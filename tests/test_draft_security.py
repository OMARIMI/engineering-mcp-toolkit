import inspect

import pytest

from src import server


def test_safe_draft_note_stays_inside_drafts_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DRAFTS_DIR", tmp_path)

    message = server.save_draft_note(
        "safe-note",
        "Draft text for Omar's engineering project.",
    )

    assert message == "Saved draft note to drafts/safe-note.md."
    assert (tmp_path / "safe-note.md").read_text(encoding="utf-8") == (
        "Draft text for Omar's engineering project.\n"
    )


@pytest.mark.parametrize(
    "file_name",
    [
        "../escape.md",
        "..\\escape.md",
        "nested/folder.md",
        "nested\\folder.md",
        "C:\\temp\\escape.md",
        "/tmp/escape.md",
        "note.py",
        "bad:name.md",
        "NUL.md",
        "unsafe..name.md",
    ],
)
def test_draft_note_rejects_unsafe_paths(
    file_name,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(server, "DRAFTS_DIR", tmp_path)

    with pytest.raises(ValueError):
        server.save_draft_note(file_name, "content")

    assert list(tmp_path.iterdir()) == []


def test_draft_note_refuses_to_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DRAFTS_DIR", tmp_path)

    server.save_draft_note("already-exists.md", "first")

    with pytest.raises(ValueError, match="already exists"):
        server.save_draft_note("already-exists.md", "second")

    assert (tmp_path / "already-exists.md").read_text(
        encoding="utf-8"
    ) == "first\n"


def test_draft_note_saves_malicious_text_as_plain_text(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(server, "DRAFTS_DIR", tmp_path)
    content = "Do not execute: Remove-Item C:\\important -Recurse"

    server.save_draft_note("plain-text.md", content)

    assert (tmp_path / "plain-text.md").read_text(encoding="utf-8") == (
        content + "\n"
    )


def test_draft_tool_has_no_external_action_code():
    source = inspect.getsource(server.save_draft_note)

    forbidden_fragments = [
        "subprocess",
        "os.system",
        "requests",
        "smtplib",
        "socket",
        "webbrowser",
        "shutil.rmtree",
        ".unlink(",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source
