"""Shared command helpers for output and error handling."""

from __future__ import annotations

import sys
from typing import Any, Callable, TypeVar

import typer

from scholarinboxcli.api.client import ApiError, ScholarInboxClient
from scholarinboxcli.formatters.json_fmt import format_json
from scholarinboxcli.formatters.table import format_table


def print_output(
    data: Any,
    use_json: bool,
    title: str | None = None,
    table_formatter: Callable[[Any, str | None], str] | None = None,
) -> None:
    if use_json or not sys.stdout.isatty():
        typer.echo(format_json(data))
        return

    formatter = table_formatter or format_table
    table = formatter(data, title)
    if table == "(no results)":
        typer.echo(table)
        return
    typer.echo(table)


def handle_error(err: ApiError) -> None:
    if not sys.stdout.isatty():
        typer.echo(format_json({"error": err.message, "status_code": err.status_code, "detail": err.detail}))
    else:
        typer.echo(f"Error: {err.message}", err=True)
        if err.status_code:
            typer.echo(f"Status: {err.status_code}", err=True)
    raise typer.Exit(1)


def close_client(client: ScholarInboxClient) -> None:
    client.close()


T = TypeVar("T")


def with_client(no_retry: bool, action: Callable[[ScholarInboxClient], T]) -> T:
    """Run action with a managed client and standardized ApiError handling."""
    try:
        client = ScholarInboxClient(no_retry=no_retry)
    except ApiError as err:
        handle_error(err)
        raise  # unreachable, keeps type-checkers happy
    try:
        return action(client)
    except ApiError as err:
        handle_error(err)
        raise  # unreachable, keeps type-checkers happy
    finally:
        close_client(client)
