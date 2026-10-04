# Architecture

## Purpose

The Engineering MCP Toolkit is a small MCP server for Omar's Module 6 learning project. It demonstrates how to expose deterministic local tools, a read-only resource, and a reusable prompt through the Model Context Protocol.

## Main modules

- `src/calculations.py`: pure Python math helpers for Ohm's law and power.
- `src/server.py`: MCP server registration, component lookup, draft-note safety checks, read-only resource, and comparison prompt.
- `data/components.json`: approved local component dataset with 121 records.
- `docs/ENGINEERING_NOTES.md`: markdown content served through `engineering://notes`.
- `tests/`: automated tests for calculations, MCP capability registration, component lookup, and draft safety.

## MCP surface

Tools:

- `calculate_current(voltage, resistance)`
- `calculate_power(voltage, current)`
- `lookup_component(query, category=None, max_cost=None, required_voltage=None, limit=5)`
- `save_draft_note(file_name, content)`

Resource:

- `engineering://notes`

Prompt:

- `compare_components(component_a, component_b, project_goal="general engineering project")`

## Data flow

1. MCP client calls a registered tool, resource, or prompt.
2. The server handles the request locally.
3. Calculations return deterministic text.
4. Component lookup reads `data/components.json` and returns matching approved records.
5. Draft creation validates the requested file name and creates a new file only inside `drafts/`.
6. The notes resource returns fixed markdown from `docs/ENGINEERING_NOTES.md`.

## Design choices

- Keep the project simple enough for learning and portfolio review.
- Preserve the local component dataset instead of replacing it with sample data.
- Use explicit validation around the only write-capable tool.
- Keep tests focused on behavior, safety boundaries, and MCP registration.
