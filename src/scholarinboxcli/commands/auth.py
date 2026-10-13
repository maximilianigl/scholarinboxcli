"""Authentication command group."""

from __future__ import annotations

import sys

import typer

from scholarinboxcli.commands.common import print_output, with_client
from scholarinboxcli.formatters.domain_tables import format_auth_status


app = typer.Typer(help="Authentication commands", no_args_is_help=True)


def _read_secret() -> str:
    # Read from a hidden prompt or a pipe so the secret stays out of shell history and argv.
    if sys.stdin.isatty():
        return typer.prompt("Magic login URL or sha_key", hide_input=True)
    return sys.stdin.readline()


@app.command("login")
def auth_login(
    url: str | None = typer.Option(
        None, "--url", help="Magic login URL with sha_key (omit to enter it at a hidden prompt or via stdin)"
    ),
):
    secret = (url or _read_secret()).strip()
    if not secret:
        typer.echo("No magic login URL or sha_key given", err=True)
        raise typer.Exit(1)

    def action(client):
        if secret.startswith(("https://", "http://")):
            client.login_with_magic_link(secret)
        else:
            client.login_with_sha_key(secret)
        typer.echo("Login successful")

    with_client(False, action)


@app.command("status")
def auth_status(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    def action(client):
        data = client.session_info()
        print_output(data, json_output, title="Session", table_formatter=format_auth_status)

    with_client(False, action)


@app.command("logout")
def auth_logout():
    from scholarinboxcli.config import Config, save_config

    save_config(Config())
    typer.echo("Logged out")
