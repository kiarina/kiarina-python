from dataclasses import dataclass

from kiarina.agi.file_info import (
    AudioFileInfo,
    FileInfo,
    ImageFileInfo,
    OtherFileInfo,
    PDFFileInfo,
    TextFileInfo,
    VideoFileInfo,
)
from kiarina.utils.file import FileBlob


@dataclass
class BuildResult:
    file_info: FileInfo
    file_blob: FileBlob
    intermediate_file_blob: FileBlob | None = None

    @property
    def text_file_info(self) -> TextFileInfo:
        if not isinstance(self.file_info, TextFileInfo):
            raise TypeError("file_info is not a TextFileInfo")
        return self.file_info

    @property
    def image_file_info(self) -> ImageFileInfo:
        if not isinstance(self.file_info, ImageFileInfo):
            raise TypeError("file_info is not an ImageFileInfo")
        return self.file_info

    @property
    def audio_file_info(self) -> AudioFileInfo:
        if not isinstance(self.file_info, AudioFileInfo):
            raise TypeError("file_info is not an AudioFileInfo")
        return self.file_info

    @property
    def video_file_info(self) -> VideoFileInfo:
        if not isinstance(self.file_info, VideoFileInfo):
            raise TypeError("file_info is not a VideoFileInfo")
        return self.file_info

    @property
    def pdf_file_info(self) -> PDFFileInfo:
        if not isinstance(self.file_info, PDFFileInfo):
            raise TypeError("file_info is not a PDFFileInfo")
        return self.file_info

    @property
    def other_file_info(self) -> OtherFileInfo:
        if not isinstance(self.file_info, OtherFileInfo):
            raise TypeError("file_info is not an OtherFileInfo")
        return self.file_info
