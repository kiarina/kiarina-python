import json

from kiarina.agi.message import ToolCall
from kiarina.agi.pre_hook import PreHookContext, PreHookError, prehook
from kiarina.i18n import get_i18n

from .._i18n import ConfirmHookI18n


@prehook
async def ConfirmPreHook(ctx: PreHookContext) -> None:
    t = get_i18n(ConfirmHookI18n, ctx.run_context.language)

    _display_tool_info(ctx.tool_call)

    while True:
        response = input(t.prompt_message).strip().lower()

        if not response:
            response = "yes"

        if response in ["yes", "y"]:
            return

        if response in ["no", "n"]:
            reason = input(t.reason_prompt).strip()

            if reason:
                raise PreHookError(t.user_rejected_with_reason.format(reason=reason))
            else:
                raise PreHookError(t.user_rejected)

        print(t.invalid_response)


def _display_tool_info(tool_call: ToolCall) -> None:
    print("\n" + "=" * 80)
    print(f"Tool: {tool_call.name}")

    if action := tool_call.args.get("action"):
        print(f"Action: {action}")

    if reason := tool_call.args.get("reason"):
        print(f"Reason: {reason}")

    if expect := tool_call.args.get("expect"):
        print(f"Expected: {expect}")

    print("\nArguments:")
    print(json.dumps(tool_call.args, indent=2, ensure_ascii=False))
    print("=" * 80)
