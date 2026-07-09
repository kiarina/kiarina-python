import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.chat_model import (
    ChatModel,
    ChatOptions,
    chat_model_registry,
    run_chat,
)
from kiarina.agi.chat_provider import TokenOverflowError
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.event import Event, message_to_event
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from .._services.prompt_registry import prompt_registry
from .._types.prompt import Prompt
from .._types.prompt_options import PromptOptions

logger = logging.getLogger(__name__)


async def run_prompt(
    history: History,
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    chat_options = chat_options or {}
    prompt_options = prompt_options or {}
    cost_recorder = cost_recorder or NullCostRecorder()

    chat_model = chat_options.get("chat_model")

    if not isinstance(chat_model, ChatModel):
        chat_model = chat_model_registry.resolve(chat_model)

    prompt = prompt_options.get("prompt")

    if not isinstance(prompt, Prompt):
        prompt = prompt_registry.resolve(prompt)

    limits = prompt_options.get("limits")

    if limits is None:
        limits = chat_model.get_capabilities()
    elif isinstance(limits, str):
        limits = ChatLimits.from_specifier(limits)

    run_context = run_context.with_metadata(
        prompt=f"{prompt}",
    )

    section_container = await prompt.get_section_container(
        history=history,
        chat_options={**chat_options, "chat_model": chat_model},
        cost_recorder=cost_recorder,
        run_context=run_context,
        **kwargs,
    )

    if not section_container.sections:  # pragma: no cover
        raise ValueError("Section is not defined")

    async for event in section_container.prepare():
        yield event

    token_scale_factor = chat_model.token_scale_factor
    request_count = 0

    while True:
        limits = limits.model_copy(
            update={
                "token_count_limit": int(limits.token_count_limit * token_scale_factor)
            }
        )

        estimates = section_container.get_estimates()

        if estimates.token_count > limits.token_count_limit:
            if not section_container.is_resizable():
                raise TokenOverflowError(estimates.token_count)

            async for event in section_container.resize(limits.token_count_limit):
                yield event

            continue

        messages = section_container.get_messages()

        async for event in section_container.ready():
            yield event

        try:
            async for ai_message in run_chat(
                messages,
                tool_infos=section_container.get_tool_infos(),
                chat_options={
                    "chat_model": chat_model,
                    "tool_choice": chat_options.get("tool_choice"),
                    "parallel_tool_calls": chat_options.get("parallel_tool_calls"),
                    "streaming": chat_options.get("streaming"),
                },
                cost_recorder=cost_recorder,
                run_context=run_context.with_metadata(
                    section_container=f"{section_container}",
                    messages=f"{len(messages)} messages, {estimates} / {limits}",
                    token_count=estimates.token_count,
                ),
            ):
                yield message_to_event(ai_message)

            break

        except TokenOverflowError as e:
            logger.warning(
                f"TokenOverflowError: {e}, "
                f"request_count={request_count}, "
                f"limits={limits.token_count_limit}, "
                f"estimates={estimates.token_count}, "
                f"scale_factor={token_scale_factor}"
            )

            if request_count >= 5:
                raise

            if e.token_count > 0:
                token_count = e.token_count
            else:
                token_count = int(estimates.token_count * (1.1 + 0.1 * request_count))

            token_scale_factor = (
                estimates.token_count / token_count * (1.0 - 0.01 * request_count)
            )
            request_count += 1

            logger.warning(
                f"Retrying with token_scale_factor={token_scale_factor:.3f}. sleep..."
            )

            await asyncio.sleep(0.1 * request_count)

        except Exception as e:
            logger.error(
                "An unexpected error occurred during prompt execution.", exc_info=e
            )
            raise e
