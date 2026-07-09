from html import escape

from kiarina.agi.audio_consumer import AudioEvent
from kiarina.agi.audio_consumer_impl.ambient import AmbientAudioEvent
from kiarina.agi.audio_event_bundler import BaseAudioEventBundler
from kiarina.agi.embedding import calc_cosine_similarity
from kiarina.agi.file_bundle import FileBundle, FileBundleTextContent

from .._settings import AmbientAudioEventBundlerSettings


class AmbientAudioEventBundler(BaseAudioEventBundler):
    def __init__(self, settings: AmbientAudioEventBundlerSettings) -> None:
        super().__init__()
        self.settings: AmbientAudioEventBundlerSettings = settings

    def bundle(self, events: list[AudioEvent]) -> FileBundle | None:
        ambient_events = [
            event for event in events if isinstance(event, AmbientAudioEvent)
        ]

        if not ambient_events:
            return None

        ambient_text = _format_ambient(
            ambient_events,
            change_similarity_threshold=self.settings.change_similarity_threshold,
        )

        return FileBundle.create(
            manifest_contents=[
                FileBundleTextContent(text=ambient_text, visibility="always"),
            ],
        )


def _format_ambient(
    events: list[AmbientAudioEvent],
    *,
    change_similarity_threshold: float,
) -> str:
    entries: list[str] = []
    previous_event: AmbientAudioEvent | None = None

    for index, event in enumerate(events, 1):
        lines = [
            str(index),
            (
                f"{_format_srt_timestamp(event.start_timestamp)} --> "
                f"{_format_srt_timestamp(event.end_timestamp)}"
            ),
        ]

        similarity = (
            None
            if previous_event is None
            else calc_cosine_similarity(previous_event.embedding, event.embedding)
        )

        if similarity is not None:
            lines.append(f'<similarity previous="{similarity:.3f}" />')

            if similarity < change_similarity_threshold:
                lines.append(
                    f'<change similarity="{similarity:.3f}">ambience changed</change>'
                )

        lines.append("<audio_tags>")

        for prediction in event.predictions:
            label = escape(prediction.label)
            lines.append(f"[{label}] {prediction.score:.3f}")

        lines.append("</audio_tags>")
        entries.append("\n".join(lines))
        previous_event = event

    return "<ambient>\n" + "\n\n".join(entries) + "\n</ambient>"


def _format_srt_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0

    total_milliseconds = round(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3600 * 1000)
    minutes, remainder = divmod(remainder, 60 * 1000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
