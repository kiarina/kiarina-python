from typing import Literal

PyannoteOutputKind = Literal[
    "auto",
    "powerset_log_probs",
    "powerset_probs",
    "powerset_logits",
    "multilabel",
]
