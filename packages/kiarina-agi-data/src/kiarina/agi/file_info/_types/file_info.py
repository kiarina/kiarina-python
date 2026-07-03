from .._models.audio_file_info import AudioFileInfo
from .._models.image_file_info import ImageFileInfo
from .._models.other_file_info import OtherFileInfo
from .._models.pdf_file_info import PDFFileInfo
from .._models.text_file_info import TextFileInfo
from .._models.video_file_info import VideoFileInfo

FileInfo = (
    TextFileInfo
    | ImageFileInfo
    | AudioFileInfo
    | VideoFileInfo
    | PDFFileInfo
    | OtherFileInfo
)
