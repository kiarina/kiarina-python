from kiarina.agi.audio_consumer import AudioEvent
from kiarina.agi.audio_consumer_impl.stt import STTAudioEvent
from kiarina.agi.audio_event_bundler import BaseAudioEventBundler
from kiarina.agi.file_bundle import FileBundle, FileBundleTextContent

from .._settings import STTAudioEventBundlerSettings


class STTAudioEventBundler(BaseAudioEventBundler):
    def __init__(self, settings: STTAudioEventBundlerSettings) -> None:
        super().__init__()
        self.settings: STTAudioEventBundlerSettings = settings

    def bundle(self, events: list[AudioEvent]) -> FileBundle | None:
        stt_events = [event for event in events if isinstance(event, STTAudioEvent)]

        if not stt_events:
            return None

        transcript = _format_transcript(stt_events)

        return FileBundle.create(
            manifest_contents=[
                FileBundleTextContent(text=transcript, visibility="unsupported"),
            ],
        )


def _format_transcript(events: list[STTAudioEvent]) -> str:
    entries: list[str] = []

    for index, event in enumerate(events, 1):
        speech = event.speech
        text = event.text
        label = ""

        if event.embedding:
            if speech.kind == "unknown_silence":
                label = "[silence] "
            elif speech.kind == "unknown_overlap":
                label = "[overlap] "
            else:
                label = f"[Speaker {speech.speaker_index + 1}] "

        start = _format_srt_timestamp(speech.start_timestamp)
        end = _format_srt_timestamp(speech.end_timestamp)
        entries.append(f"{index}\n{start} --> {end}\n{label}{text}")

    return "<transcript>\n" + "\n\n".join(entries) + "\n</transcript>"


def _format_srt_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0

    total_milliseconds = round(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3600 * 1000)
    minutes, remainder = divmod(remainder, 60 * 1000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
