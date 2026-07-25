from collections.abc import Iterator

import pytest

from kiarina.agi.prompt import BasePrompt, prompt_registry
from kiarina.agi.section_container import SectionContainer


@pytest.fixture(autouse=True)
def cleanup() -> Iterator[None]:
    yield
    prompt_registry.clear()


def test_prompt_registry() -> None:

    class ExamplePrompt(BasePrompt):
        async def get_section_container(self, **kwargs: object) -> SectionContainer:
            raise NotImplementedError

    prompt_registry.register("test", ExamplePrompt)

    prompt = prompt_registry.create("test")
    assert isinstance(prompt, ExamplePrompt)
    assert prompt.name == "test"
