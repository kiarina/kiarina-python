import numpy as np

from kiarina.agi.audio_tagging_model import tag_audio
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


async def test_tag_audio(run_context: RunContext, cost_recorder: CostRecorder) -> None:
    result = await tag_audio(
        np.zeros(1600),
        16000,
        audio_tagging_options={
            "audio_tagging_model": "mock",
        },
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    labels = [p.label for p in result]
    assert labels == ["Speech", "Music", "Silence"]
    assert result[0].score == 0.9


async def test_tag_audio_top_k(run_context: RunContext) -> None:
    result = await tag_audio(
        np.zeros(1600),
        16000,
        audio_tagging_options={
            "audio_tagging_model": "mock",
            "top_k": 2,
        },
        run_context=run_context,
    )

    assert len(result) == 2
    assert result[0].label == "Speech"


async def test_tag_audio_threshold(run_context: RunContext) -> None:
    result = await tag_audio(
        np.zeros(1600),
        16000,
        audio_tagging_options={
            "audio_tagging_model": "mock",
            "threshold": 0.5,
        },
        run_context=run_context,
    )

    assert [p.label for p in result] == ["Speech"]


async def test_tag_audio_sorts_desc(run_context: RunContext) -> None:
    # mock provider returns predictions in declared order; tag_audio must sort.
    result = await tag_audio(
        np.zeros(1600),
        16000,
        audio_tagging_options={
            "audio_tagging_model": "mock",
        },
        run_context=run_context,
    )

    scores = [p.score for p in result]
    assert scores == sorted(scores, reverse=True)
