# Engineering MCP Toolkit

Module 6 project for Omar's AI Engineering Learning Pathway.

This project is a local Model Context Protocol (MCP) server for small engineering workflows. It exposes safe tools for electrical calculations, approved component lookup, and draft-note creation.

## MCP capabilities

Tools:

- `calculate_current`
- `calculate_power`
- `lookup_component`
- `save_draft_note`

Resource:

- `engineering://notes`

Prompt:

- `compare_components`

## Dataset

The project uses the existing real local dataset at `data/components.json`.

Current verified dataset size: 121 component records.

## Setup

```powershell
pip install -r requirements.txt
```

## Test

```powershell
python -m pytest -q
```

## Run the MCP server

```powershell
mcp run .\src\server.py
```

For interactive inspection:

```powershell
mcp dev .\src\server.py
```

## Safety boundary

`save_draft_note` can only create new `.md` or `.txt` files inside `drafts/`. It rejects path traversal, absolute paths, nested paths, Windows drive syntax, unsafe file names, unsupported extensions, reserved device names, blank content, oversized content, and overwrites.

The draft tool writes plain text only. It does not delete files, execute shell commands, access arbitrary files, send messages, make purchases, or control devices.

Generated draft contents are ignored by Git so private notes do not get published by accident.
