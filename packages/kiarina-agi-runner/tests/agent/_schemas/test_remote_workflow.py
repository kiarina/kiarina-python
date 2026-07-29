import pytest
from pydantic import ValidationError

from kiarina.agi.agent import RemoteWorkflowRequest, RemoteWorkflowResult
from kiarina.agi.event import AIMessageEvent, HumanMessageEvent
from kiarina.agi.history import History


def test_remote_workflow_contract_round_trip() -> None:
    request = RemoteWorkflowRequest(
        request_id="request-1",
        history=History(events=[HumanMessageEvent.create("hello")]),
        metadata={"transport": "test"},
    )
    parsed_request = RemoteWorkflowRequest.model_validate_json(
        request.model_dump_json()
    )

    assert parsed_request.history.get_messages()[0].to_text() == "hello"
    assert parsed_request.metadata == {"transport": "test"}

    result = RemoteWorkflowResult(
        request_id=request.request_id,
        status="completed",
        events=[AIMessageEvent.create("world")],
    )
    parsed_result = RemoteWorkflowResult.model_validate_json(result.model_dump_json())

    assert parsed_result.events[0].type == "ai_message"
    assert parsed_result.events[0].to_text() == "world"


def test_remote_workflow_failed_result_requires_error() -> None:
    with pytest.raises(ValidationError, match="Failed result requires an error"):
        RemoteWorkflowResult(request_id="request-1", status="failed")
