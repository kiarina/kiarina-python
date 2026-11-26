import sys
from pathlib import Path
from types import ModuleType

import pytest

from kiarina.agi.chat_provider_impl.codex import (
    CodexChatProvider,
    CodexChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.codex._operations.find_codex_bin import (
    find_codex_bin,
)


@pytest.fixture
def no_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "codex_cli_bin", None)


@pytest.fixture
def bundle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    module = ModuleType("codex_cli_bin")
    module.bundled_codex_path = lambda: tmp_path / "bundled" / "codex"  # type: ignore[attr-defined]
    module.bundled_path_dir = lambda: tmp_path / "bundled" / "codex-path"  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "codex_cli_bin", module)
    return tmp_path / "bundled"


def _install_codex(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    # shutil.which wants an extension from PATHEXT on Windows.
    path = directory / ("codex.exe" if sys.platform == "win32" else "codex")
    path.write_text("")
    path.chmod(0o755)
    return path


def test_setting_comes_first(bundle: Path, tmp_path: Path) -> None:
    _install_codex(tmp_path / "bin")
    env = {"PATH": str(tmp_path / "bin")}

    assert find_codex_bin("/opt/codex", env) == ("/opt/codex", None)


def test_bundle_comes_before_path(bundle: Path, tmp_path: Path) -> None:
    _install_codex(tmp_path / "bin")
    env = {"PATH": str(tmp_path / "bin")}

    assert find_codex_bin(None, env) == (str(bundle / "codex"), bundle / "codex-path")


@pytest.mark.usefixtures("no_bundle")
def test_setting_without_bundle() -> None:
    assert find_codex_bin("/opt/codex", {"PATH": ""}) == ("/opt/codex", None)


@pytest.mark.usefixtures("no_bundle")
def test_path_without_bundle(tmp_path: Path) -> None:
    installed = _install_codex(tmp_path / "bin")

    assert find_codex_bin(None, {"PATH": str(tmp_path / "bin")}) == (
        str(installed),
        None,
    )


@pytest.mark.usefixtures("no_bundle")
def test_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError) as exc_info:
        find_codex_bin(None, {"PATH": str(tmp_path)})

    message = str(exc_info.value)
    assert "kiarina-agi-text[chat-provider-codex]" in message
    assert "PATH" in message
    assert "codex_bin" in message


@pytest.mark.usefixtures("no_bundle")
def test_provider_without_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    installed = _install_codex(tmp_path / "bin")
    (tmp_path / "models_cache.json").write_text('{"models": [{"slug": "gpt-6.2-sol"}]}')
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))

    settings = CodexChatProviderSettings(codex_home=str(tmp_path))

    with pytest.raises(FileNotFoundError):
        _ = CodexChatProvider(settings).codex_bin

    with pytest.raises(FileNotFoundError):
        CodexChatProvider(settings).create_session(tmp_path)

    # `env` of the settings is searched too.
    provider = CodexChatProvider(
        settings.model_copy(update={"env": {"PATH": str(tmp_path / "bin")}})
    )

    assert provider.codex_bin == str(installed)
    assert provider.create_session(tmp_path)._args[0] == str(installed)

    provider = CodexChatProvider(settings.model_copy(update={"codex_bin": "/x/codex"}))

    assert provider.codex_bin == "/x/codex"
    assert provider.create_session(tmp_path)._args[0] == "/x/codex"
