# scholarinboxcli

Scholar Inbox CLI: digests, search, collections, and bookmarks for humans and agents alike.

## Installation

```bash
pip install scholarinboxcli
```

Or with uv:

```bash
uv pip install scholarinboxcli
```

Or run directly with uvx (no install):

```bash
uvx scholarinboxcli auth login
```

To install this fork (with `rate`), pin a reviewed commit rather than tracking the branch:

```bash
uv tool install "git+https://github.com/maximilianigl/scholarinboxcli.git@<commit>"
```

## Auth

The `sha_key` in the magic link is a long-lived login credential. Anyone who has it can sign in as you.

```bash
# Paste the magic-link URL or the bare sha_key at a hidden prompt
scholarinboxcli auth login

# Or pipe it in, e.g. from the clipboard
pbpaste | scholarinboxcli auth login

# --url still works, but puts the key in shell history and the process list
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY"

# Check current session and user info
scholarinboxcli auth status

# Clear local session config
scholarinboxcli auth logout
```

The session is stored at `~/.config/scholarinboxcli/config.json` with owner-only permissions (`0600`). You can override the API base with `SCHOLAR_INBOX_API_BASE`; it must use `https://` (plain `http://` is allowed only for localhost).

## Command reference

Top-level commands:

- `auth` (login/status/logout)
- `digest`
- `trending`
- `search`
- `semantic`
- `rate` *(fork only — rate papers)*
- `interactions`
- `bookmark` (list/add/remove)
- `collection` (list/create/rename/delete/add/remove/papers/similar)
- `conference` (list/explore)

Run `scholarinboxcli --help` or `scholarinboxcli <command> --help` for full options.

## Quickstart

```bash
# Fetch a daily digest by date (MM-DD-YYYY)
scholarinboxcli digest --date 01-30-2026 --json

# Trending papers (last 7 days)
scholarinboxcli trending --category ALL --days 7 --json

# Keyword search
scholarinboxcli search "transformers" --limit 5 --json

# Semantic search
scholarinboxcli semantic "graph neural networks" --limit 5 --json

# List your bookmarks
scholarinboxcli bookmark list --json
```

## Collections

```bash
# List collections
scholarinboxcli collection list

# Expanded collection names (marks which collections are expanded server-side)
scholarinboxcli collection list --expanded

# Create, rename, delete
scholarinboxcli collection create "My Collection"

# Rename by ID (or name)
scholarinboxcli collection rename 10759 "New Name"

# Delete by ID (or name)
scholarinboxcli collection delete 10759

# Add/remove papers
scholarinboxcli collection add 10759 4559909
scholarinboxcli collection remove 10759 4559909

# Show papers in a collection
scholarinboxcli collection papers 10759

# Similar papers for one or more collections
scholarinboxcli collection similar 10759 12345

# Optional local sorting for display (e.g., newest first)
scholarinboxcli collection similar "AIAgents" --sort year

# Sort ascending instead
scholarinboxcli collection similar "AIAgents" --sort year --asc

# You can also use collection names (case-insensitive). The CLI will
# automatically fetch collection ID mappings from the API when needed.
scholarinboxcli collection papers "AIAgents"
scholarinboxcli collection similar "AIAgents" "Benchmark"
```

Collection name matching is exact → prefix → contains. If multiple matches exist, the CLI reports ambiguity and shows candidate IDs.
`collection similar` supports client-side sorting with `--sort year|title` and optional `--asc`.

## Search

```bash
# Full-text keyword search
scholarinboxcli search "transformers" --limit 5
```

## Semantic Search

```bash
# Semantic similarity search
scholarinboxcli semantic "graph neural networks" --limit 5
```

## Rate Papers *(fork only)*

```bash
# Upvote a paper
scholarinboxcli rate PAPER_ID 1

# Downvote a paper
scholarinboxcli rate PAPER_ID -1

# Remove your rating
scholarinboxcli rate PAPER_ID 0
```

Get paper IDs from the `_id` field in search/digest/trending/similar results.

## Other commands

```bash
# Daily digest view (MM-DD-YYYY)
scholarinboxcli digest --date 01-30-2026

# Trending papers by category
scholarinboxcli trending --category ALL --days 7

# Read/like/dislike interactions feed
scholarinboxcli interactions --type all

# List bookmarks
scholarinboxcli bookmark list

# List known conferences
scholarinboxcli conference list

# Explore conference indices
scholarinboxcli conference explore
```

## Output modes

- TTY: Rich tables
- `--json`: pretty JSON
- Piped: pretty JSON (auto)

Examples for agents/scripting:

```bash
# Auto-JSON when piped
scholarinboxcli collection list | jq '.'

# Explicit JSON output
scholarinboxcli collection papers "AIAgents" --json

# JSON for automation (stable keys)
scholarinboxcli search "diffusion" --json
```

## Notes

- Some collection mutations (create/rename/delete/add/remove) rely on best-effort endpoints that may change on the service side. If a mutation fails, try again or use the web UI to validate the current behavior.
- Bookmarks are stored as a dedicated collection named "Bookmarks" in the web app; `bookmark list` pulls that collection via `/api/get_collections`.
- Similar papers for collections uses the server endpoint used by the web UI. Results typically appear under `digest_df` in JSON responses.

## License

MIT. See `LICENSE`.
