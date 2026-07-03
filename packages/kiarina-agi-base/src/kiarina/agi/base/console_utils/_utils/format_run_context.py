from kiarina.agi.base.run_context import RunContext


def format_run_context(run_context: RunContext) -> str:
    lines = [
        f"organization_id: {run_context.organization_id}",
        f"user_id: {run_context.user_id}",
        f"agent_id: {run_context.agent_id}",
        f"node_id: {run_context.node_id}",
        f"time_zone: {run_context.time_zone}",
        f"language: {run_context.language}",
        f"currency: {run_context.currency}",
    ]

    for k, v in run_context.metadata.items():
        lines.append(f"{k}: {v}")

    return "\n".join(lines)
