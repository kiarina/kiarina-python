from typing import Any

from kiarina.lib.google import get_self_signed_jwt


def test_get_self_signed_jwt(load_settings: Any) -> None:
    jwt = get_self_signed_jwt(
        "service_account_file",
        audience="https://blazeworks.jp/",
    )
    assert jwt.count(".") == 2
