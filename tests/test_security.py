import stat

import pytest
from typer.testing import CliRunner

from scholarinboxcli import config
from scholarinboxcli.api import client as client_mod
from scholarinboxcli.api.client import ApiError, ScholarInboxClient
from scholarinboxcli.cli import app
from scholarinboxcli.commands import common


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    config_dir = tmp_path / "scholarinboxcli"
    monkeypatch.setattr(config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config, "CONFIG_PATH", config_dir / "config.json")
    monkeypatch.setattr(client_mod, "load_config", config.load_config)
    monkeypatch.setattr(client_mod, "save_config", config.save_config)
    return config_dir


def test_save_config_is_owner_only_even_if_file_was_world_readable(tmp_config):
    tmp_config.mkdir(mode=0o755)
    (tmp_config / "config.json").write_text("{}")
    (tmp_config / "config.json").chmod(0o644)

    config.save_config(config.Config(cookies=[{"name": "session", "value": "secret"}]))

    assert stat.S_IMODE((tmp_config / "config.json").stat().st_mode) == 0o600
    assert stat.S_IMODE(tmp_config.stat().st_mode) == 0o700
    assert config.load_config().cookies == [{"name": "session", "value": "secret"}]


def test_insecure_api_base_is_rejected(tmp_config, monkeypatch):
    monkeypatch.setenv("SCHOLAR_INBOX_API_BASE", "http://api.scholar-inbox.com")
    with pytest.raises(ApiError):
        ScholarInboxClient()


def test_localhost_api_base_is_allowed(tmp_config, monkeypatch):
    monkeypatch.setenv("SCHOLAR_INBOX_API_BASE", "http://localhost:8000")
    ScholarInboxClient().close()


def test_sha_key_is_url_encoded_into_login_path(tmp_config, monkeypatch):
    client = ScholarInboxClient()
    paths = []

    class _Resp:
        status_code = 200

    monkeypatch.setattr(client.client, "get", lambda path: paths.append(path) or _Resp())
    client.login_with_sha_key("../logout?x=1")

    assert paths == ["/api/login/..%2Flogout%3Fx%3D1/"]


def test_magic_link_without_sha_key_must_be_scholar_inbox_https(tmp_config):
    client = ScholarInboxClient()
    for url in ("https://evil.example/login", "http://www.scholar-inbox.com/login", "https://scholar-inbox.com.evil.example/"):
        with pytest.raises(ApiError):
            client.login_with_magic_link(url)


def test_login_reads_secret_from_stdin(monkeypatch):
    calls = []

    class _FakeClient:
        def __init__(self, no_retry: bool = False):
            pass

        def login_with_sha_key(self, sha_key):
            calls.append(("sha_key", sha_key))

        def login_with_magic_link(self, url):
            calls.append(("url", url))

        def close(self):
            pass

    monkeypatch.setattr(common, "ScholarInboxClient", _FakeClient)
    runner = CliRunner()

    assert runner.invoke(app, ["auth", "login"], input="abc123\n").exit_code == 0
    url = "https://www.scholar-inbox.com/login?sha_key=abc123&date=01-01-2026"
    assert runner.invoke(app, ["auth", "login"], input=url + "\n").exit_code == 0
    assert runner.invoke(app, ["auth", "login"], input="\n").exit_code == 1
    assert calls == [("sha_key", "abc123"), ("url", url)]
