# Permissions and Safety

## Capability classification

`calculate_current`

- Type: deterministic calculation
- Access: no file, network, shell, browser, purchase, messaging, or device access
- Risk: low

`calculate_power`

- Type: deterministic calculation
- Access: no file, network, shell, browser, purchase, messaging, or device access
- Risk: low

`lookup_component`

- Type: local read-only dataset lookup
- Access: reads only `data/components.json`
- Risk: low

`engineering://notes`

- Type: read-only MCP resource
- Access: reads fixed project notes only
- Risk: low

`compare_components`

- Type: MCP prompt template
- Access: no direct file, network, shell, browser, purchase, messaging, or device access
- Risk: low

`save_draft_note`

- Type: restricted local write
- Access: creates new `.md` or `.txt` files inside `drafts/`
- Risk: medium because it writes files, reduced by strict path and overwrite controls

## Draft-note restrictions

The draft tool:

- rejects path traversal such as `../note.md`
- rejects absolute paths and Windows drive syntax
- rejects nested paths
- rejects null bytes
- rejects unsafe characters
- rejects reserved Windows device names
- accepts only `.md` and `.txt`
- creates files with exclusive create mode
- refuses to overwrite existing files
- enforces a maximum content size
- writes content as plain text

The draft tool does not:

- delete files
- overwrite arbitrary files
- run shell commands
- import or call messaging services
- make purchases
- control devices
- browse the web
- read unrestricted files

## Secret handling

Do not commit API keys, passwords, tokens, private data, confidential files, `.env` files, generated caches, or private draft contents.
