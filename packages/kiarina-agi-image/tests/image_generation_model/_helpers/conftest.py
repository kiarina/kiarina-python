# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import pytest

from kiarina.agi.image_generation_model import settings_manager


@pytest.fixture(autouse=True)
def setup():
    settings_manager.cli_args = settings_manager.settings_cls().model_dump()
    yield
    settings_manager.cli_args = {}


def pytest_generate_tests(metafunc):
    if "image_generation_model_name" in metafunc.fixturenames:
        cases = []

        for i, image_generation_model_name in enumerate(
            settings_manager.settings_cls().presets.keys()
        ):
            cases.append(
                pytest.param(
                    image_generation_model_name,
                    id=f"{i:02d}. {image_generation_model_name}",
                )
            )

        metafunc.parametrize("image_generation_model_name", cases)
