import pytest

from kiarina.agi.base.run_context import RunContext


@pytest.mark.parametrize(
    "id_str",
    [
        "simple",
        "with-hyphen",
        "with_underscore",
        "with.dot",
        "mixed-id_v1.0",
        "123",
        "id123",
        "a",
        "A",
        "ID-123_v2.0",
        "organization.123",
        "user.456",
        "agent.v1.0",
        "runner.test",
        "organization-123",
        "user_456",
        "agent-v1_0",
        "runner_test-1",
    ],
)
def test_id_str_valid(id_str):
    RunContext(
        organization_id=id_str,
        user_id=id_str,
        agent_id=id_str,
        node_id=id_str,
    )


@pytest.mark.parametrize(
    "id_str",
    [
        "",  # Empty string
        "id@domain",
        "id with space",
        "id/path",
        "id\\path",
        "id:port",
        "id*wildcard",
        "id?query",
        'id"quote',
        "id<bracket",
        "id>bracket",
        "id|pipe",
        "id#hash",
        "id%percent",
        "id&ampersand",
        "id+plus",
        "id=equals",
        "id[bracket]",
        "id{brace}",
        "id(paren)",
        "id,comma",
        "id;semicolon",
    ],
)
def test_id_str_invalid(id_str):
    with pytest.raises(ValueError):
        RunContext(
            organization_id=id_str,
            user_id=id_str,
            agent_id=id_str,
            node_id=id_str,
        )
