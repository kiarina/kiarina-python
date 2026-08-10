from typing import TypeAlias

EventSpecifier: TypeAlias = str
"""
A string in one of the following formats:

- "{HumanMessageText}"
- "{HumanMessageSpecJSON}"
- '["human", "{HumanMessageText}"]'
- '["human", "{HumanMessageSpecJSON}"]'
- '["ai", "{AIMessageText}"]'
- '["ai", "{AIMessageSpecJSON}"]'
- '["tool", "{ToolMessageSpecJSON}"]'
- '["custom", {CustomEventPayloadJSON}]'

Formats:
- HumanMessageText: A string used as the text of a kiarina.agi.message_builder.HumanMessageSpec.text
- HumanMessageSpecJSON: A JSON string compatible with kiarina.agi.message_builder.HumanMessageSpec.
- AIMessageText: A string used as the text of a kiarina.agi.message_builder.AIMessageSpec.text
- AIMessageSpecJSON: A JSON string compatible with kiarina.agi.message_builder.AIMessageSpec.
- ToolMessageSpecJSON: A JSON string compatible with kiarina.agi.message_builder.ToolMessageSpec.
- CustomEventPayloadJSON: A JSON string compatible with kiarina.agi.event.CustomEvent.payload

Examples:
- "Hello"
- '{"text": "Hello", "files": ["/path/to/file.txt"]}'
- '["ai", "Hello"]'
- '["ai", {"text": "Hello", "tool_calls": [{"name": "hello", "args": {"message": "Hello"}}]}]'
- '["tool", {"text": "Hello", "tool_call_id": "1234", "tool_name": "hello"}]'
- '["custom", {"custom_key": "custom_value"}]'
"""
