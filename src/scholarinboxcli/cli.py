"""Scholar Inbox CLI app composition."""

from __future__ import annotations

import typer

from scholarinboxcli.commands import auth, bookmarks, collections, conferences, papers
from scholarinboxcli.services.collections import resolve_collection_id as _resolve_collection_id  # noqa: F401


app = typer.Typer(
    help=(
        "Scholar Inbox CLI.\n\n"
        "Examples:\n"
        "  scholarinboxcli auth login\n"
        "  scholarinboxcli digest --date 01-30-2026 --json\n"
        "  scholarinboxcli search \"transformers\" --limit 5 --json\n"
        "  scholarinboxcli collection papers \"AIAgents\" --json\n"
        "  scholarinboxcli conference explore --json\n"
    )
)

# Top-level feed/search commands
papers.register(app)

# Grouped commands
app.add_typer(auth.app, name="auth")
app.add_typer(collections.app, name="collection")
app.add_typer(bookmarks.app, name="bookmark")
app.add_typer(conferences.app, name="conference")
