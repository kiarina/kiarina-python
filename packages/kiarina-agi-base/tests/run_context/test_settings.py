import pytest

from kiarina.agi.run_context import RunContextSettings


def test_disallow_default_ids_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KIARINA_AGI_RUN_CONTEXT_DISALLOW_DEFAULT_IDS", "true")

    assert RunContextSettings().disallow_default_ids is True
