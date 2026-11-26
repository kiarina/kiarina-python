import shutil
from collections.abc import Mapping
from pathlib import Path


def find_codex_bin(
    codex_bin: str | None, env: Mapping[str, str]
) -> tuple[str, Path | None]:
    """
    The Codex to run, and the directory of its helper commands to put on `PATH`.

    In order: `codex_bin`, the one bundled in `openai-codex-cli-bin`, and `codex`
    on the `PATH` of `env`. The bundled one comes before `PATH` so that installing
    Codex on the machine does not change what an existing setup runs.
    """
    if codex_bin:
        return codex_bin, None

    try:
        import codex_cli_bin  # type: ignore[import-untyped]
    except ImportError:
        pass
    else:
        return str(codex_cli_bin.bundled_codex_path()), codex_cli_bin.bundled_path_dir()

    if found := shutil.which("codex", path=env.get("PATH")):
        return found, None

    raise FileNotFoundError(
        "Codex is required to use CodexChatProvider, and none was found. "
        "Do one of: install the bundled one with "
        "pip install 'kiarina-agi-text[chat-provider-codex]', "
        "install Codex so that `codex` is on PATH, "
        "or set `codex_bin` to its path."
    )
