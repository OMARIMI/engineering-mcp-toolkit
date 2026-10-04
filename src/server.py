"""Engineering MCP Toolkit server.

This server intentionally exposes a small, auditable MCP surface:
engineering calculations, approved component lookup, safe draft-note creation,
a read-only notes resource, and a reusable comparison prompt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

try:
    from src.calculations import (
        calculate_current as current_math,
        calculate_power as power_math,
    )
except ModuleNotFoundError:
    from calculations import (
        calculate_current as current_math,
        calculate_power as power_math,
    )


BASE_DIR = Path(__file__).resolve().parent.parent
COMPONENTS_PATH = BASE_DIR / "data" / "components.json"
DRAFTS_DIR = BASE_DIR / "drafts"
NOTES_PATH = BASE_DIR / "docs" / "ENGINEERING_NOTES.md"

MAX_DRAFT_CHARS = 20_000
SAFE_DRAFT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,79}$")
ALLOWED_DRAFT_SUFFIXES = {".md", ".txt"}
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


mcp = MCPServer(
    "Engineering MCP Toolkit",
    version="1.0.0",
    instructions=(
        "Use the approved local engineering tools and dataset. Draft-note "
        "creation is restricted to the project drafts folder."
    ),
)


def load_components() -> list[dict[str, Any]]:
    """Load the approved component dataset without modifying it."""

    records = json.loads(COMPONENTS_PATH.read_text(encoding="utf-8"))

    if not isinstance(records, list):
        raise ValueError("Component dataset must be a list of records.")

    return records


def _record_text(record: dict[str, Any]) -> str:
    keywords = record.get("keywords") or []

    return " ".join(
        [
            str(record.get("id", "")),
            str(record.get("name", "")),
            str(record.get("category", "")),
            str(record.get("description", "")),
            " ".join(str(keyword) for keyword in keywords),
            str(record.get("material", "")),
        ]
    ).lower()


def _format_component(record: dict[str, Any], number: int) -> list[str]:
    return [
        f"{number}. {record['name']} ({record['id']})",
        f"   Category: {record['category']}",
        (
            "   Voltage: "
            f"{record['voltage_min_v']:g}-"
            f"{record['voltage_max_v']:g} V"
        ),
        f"   Estimated cost: ${record['estimated_cost_usd']:.2f}",
        f"   Material: {record['material']}",
        f"   Source: {record['source_reference']}",
        "",
    ]


def _safe_draft_path(file_name: str) -> Path:
    if not isinstance(file_name, str):
        raise ValueError("Draft file name must be text.")

    candidate = file_name.strip()

    if not candidate:
        raise ValueError("Draft file name cannot be blank.")

    if "\x00" in candidate:
        raise ValueError("Draft file name cannot contain null bytes.")

    if "/" in candidate or "\\" in candidate or ":" in candidate:
        raise ValueError("Draft file name cannot contain paths or drives.")

    if ".." in candidate:
        raise ValueError("Draft file name cannot contain '..'.")

    path = Path(candidate)

    if path.is_absolute() or path.name != candidate:
        raise ValueError("Draft file name must be a simple file name.")

    if path.suffix == "":
        candidate = f"{candidate}.md"
        path = Path(candidate)

    if path.suffix.lower() not in ALLOWED_DRAFT_SUFFIXES:
        raise ValueError("Draft file name must end in .md or .txt.")

    if path.stem.upper() in WINDOWS_RESERVED_NAMES:
        raise ValueError("Draft file name uses a reserved system name.")

    if not SAFE_DRAFT_NAME.fullmatch(candidate):
        raise ValueError(
            "Draft file name may only use letters, numbers, spaces, "
            "dots, underscores, and hyphens."
        )

    drafts_root = DRAFTS_DIR.resolve()
    draft_path = (drafts_root / candidate).resolve()

    if draft_path.parent != drafts_root:
        raise ValueError("Draft file must stay inside the drafts folder.")

    return draft_path


@mcp.tool()
def calculate_current(
    voltage: float,
    resistance: float,
) -> str:
    """Calculate electrical current using Ohm's law."""

    current = current_math(voltage, resistance)

    return (
        f"The current is {current:g} amps. "
        f"Using Ohm's law: {voltage:g} V / "
        f"{resistance:g} ohms = {current:g} A."
    )


@mcp.tool()
def calculate_power(
    voltage: float,
    current: float,
) -> str:
    """Calculate electrical power."""

    power = power_math(voltage, current)

    return (
        f"The power is {power:g} watts. "
        f"Using P = V x I: {voltage:g} V x "
        f"{current:g} A = {power:g} W."
    )


@mcp.tool()
def lookup_component(
    query: str,
    category: str | None = None,
    max_cost: float | None = None,
    required_voltage: float | None = None,
    limit: int = 5,
) -> str:
    """Search the approved local component dataset."""

    clean_query = query.strip()

    if not clean_query:
        raise ValueError("Query cannot be blank.")

    if limit < 1 or limit > 10:
        raise ValueError("Limit must be between 1 and 10.")

    if max_cost is not None and max_cost < 0:
        raise ValueError("Maximum cost cannot be negative.")

    records = load_components()
    query_terms = {term.lower() for term in clean_query.split()}
    matches: list[dict[str, Any]] = []

    for record in records:
        if category and record["category"].lower() != category.lower():
            continue

        if max_cost is not None and record["estimated_cost_usd"] > max_cost:
            continue

        if required_voltage is not None:
            if not (
                record["voltage_min_v"]
                <= required_voltage
                <= record["voltage_max_v"]
            ):
                continue

        searchable_text = _record_text(record)
        score = sum(1 for term in query_terms if term in searchable_text)

        if score > 0:
            matches.append({"score": score, "record": record})

    matches.sort(
        key=lambda item: (
            -item["score"],
            item["record"]["estimated_cost_usd"],
            item["record"]["id"],
        )
    )

    selected = matches[:limit]

    if not selected:
        return "No components matched your search and filters."

    lines = [f"I found {len(selected)} matching component(s):", ""]

    for number, item in enumerate(selected, start=1):
        lines.extend(_format_component(item["record"], number))

    return "\n".join(lines).rstrip()


@mcp.tool()
def save_draft_note(
    file_name: str,
    content: str,
) -> str:
    """Save a plain-text draft note inside the project drafts folder only."""

    if not isinstance(content, str):
        raise ValueError("Draft content must be text.")

    if not content.strip():
        raise ValueError("Draft content cannot be blank.")

    if len(content) > MAX_DRAFT_CHARS:
        raise ValueError(
            f"Draft content cannot exceed {MAX_DRAFT_CHARS} characters."
        )

    draft_path = _safe_draft_path(file_name)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with draft_path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.write("\n")
    except FileExistsError as exc:
        raise ValueError("A draft with that name already exists.") from exc

    return f"Saved draft note to drafts/{draft_path.name}."


@mcp.resource(
    "engineering://notes",
    name="engineering_notes",
    description="Read-only notes for the Engineering MCP Toolkit.",
    mime_type="text/markdown",
)
def engineering_notes() -> str:
    """Return fixed project notes without accepting file paths."""

    if NOTES_PATH.exists():
        return NOTES_PATH.read_text(encoding="utf-8")

    component_count = len(load_components())
    return (
        "# Engineering MCP Toolkit Notes\n\n"
        f"- Approved component records: {component_count}\n"
        "- Resource is read-only and does not accept path parameters.\n"
    )


@mcp.prompt()
def compare_components(
    component_a: str,
    component_b: str,
    project_goal: str = "general engineering project",
) -> str:
    """Create a comparison prompt for two engineering components."""

    return (
        "Compare two engineering components for the stated project goal.\n\n"
        f"Component A: {component_a}\n"
        f"Component B: {component_b}\n"
        f"Project goal: {project_goal}\n\n"
        "Use lookup_component when local dataset evidence is needed. Compare "
        "category, operating voltage, cost, material, likely use case, and "
        "tradeoffs. End with a practical recommendation and mention any "
        "missing information."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
