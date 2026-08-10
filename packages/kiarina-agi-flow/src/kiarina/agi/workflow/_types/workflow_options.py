from typing import TypedDict

from .workflow import Workflow
from .workflow_specifier import WorkflowSpecifier


class WorkflowOptions(TypedDict, total=False):
    workflow: Workflow | WorkflowSpecifier | None
