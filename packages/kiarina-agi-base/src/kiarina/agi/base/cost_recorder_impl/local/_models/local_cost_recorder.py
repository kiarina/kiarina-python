import json
import logging
import os
from typing import Any

from kiarina.agi.base.cost_record import CostRecord
from kiarina.agi.base.cost_recorder import BaseCostRecorder
from kiarina.agi.base.run_context import RunContext
from kiarina.utils.app import user_directory

logger = logging.getLogger(__name__)


class LocalCostRecorder(BaseCostRecorder):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @property
    def file_path(self) -> str:
        return str(user_directory.get_user_data_dir() / "costs.jsonl")

    async def _save(self, run_context: RunContext) -> None:
        dir_path = os.path.dirname(self.file_path)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        for record in self.records:
            line = (
                json.dumps(
                    self._to_dict(record, run_context),
                    ensure_ascii=False,
                )
                + "\n"
            )

            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line)

        logger.info(f"Saved cost records to {self.file_path}")

    def _to_dict(
        self, cost_record: CostRecord, run_context: RunContext
    ) -> dict[str, Any]:
        return {
            "organization_id": run_context.organization_id,
            "user_id": run_context.user_id,
            "agent_id": run_context.agent_id,
            **cost_record.model_dump(mode="json"),
        }
