from kiarina.agi.content import Content
from kiarina.agi.display_content import FileDisplayContent, TextDisplayContent
from kiarina.agi.file_info import FileInfo
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_logger_impl.console import ConsoleToolLogger


def test_console_tool_logger(
    run_context: RunContext,
    text_file_info: FileInfo,
    image_file_info: FileInfo,
) -> None:
    tool_logger = ConsoleToolLogger()

    tool_call = ToolCall(
        id="1",
        name="run",
        args={
            "action": "run_shell",
            "reason": "test",
            "expect": "ok",
            "command": "echo hello",
        },
    )

    tool_message = ToolMessage(
        contents=[
            Content(
                text="Hello",
                files=[text_file_info, image_file_info],
            )
        ],
        tool_name="run",
        tool_call_args=tool_call.args,
        tool_call_id="1",
        return_direct=True,
        artifact={"my_artifact": "This is an artifact."},
        metadata={
            "my_metadata_1": "This is metadata 1.",
            "my_metadata_2": "This is metadata 2.",
        },
        display_contents=[
            TextDisplayContent(text="This is display content."),
            FileDisplayContent(
                mime_type=image_file_info.mime_type,
                uri_or_file_path=image_file_info.uri_or_file_path,
                display_name="sample image",
            ),
        ],
    )

    tool_logger.log_tool_start(tool_call, run_context.with_metadata(tool="run"))
    tool_logger.log_tool_end(tool_message, run_context)

    assert True
