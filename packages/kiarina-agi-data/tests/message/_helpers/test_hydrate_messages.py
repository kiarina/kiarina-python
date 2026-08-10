from kiarina.agi.file_info import ImageFileInfo, TextFileInfo
from kiarina.agi.file_info_pool import FileInfoPool
from kiarina.agi.message import HumanMessage, hydrate_messages


def test_hydrate(text_file_info: TextFileInfo, image_file_info: ImageFileInfo) -> None:
    pool: FileInfoPool = [text_file_info, image_file_info]

    message = HumanMessage.model_validate(
        {
            "contents": [
                {
                    "text": "Hello",
                    "files": [
                        text_file_info.as_metadata_only(),
                        image_file_info.as_metadata_only(),
                    ],
                },
            ]
        }
    )

    new_messages, pool = hydrate_messages([message, message], pool)

    assert len(pool) == 0

    for new_message in new_messages:
        print("--- New Message ---")
        print(new_message)

    for file_info in pool:
        print("--- Remaining File Info ---")
        print(file_info)


def test_no_files() -> None:
    message = HumanMessage.model_validate(
        {
            "contents": [
                {
                    "text": "Hello",
                },
            ]
        }
    )

    _, pool = hydrate_messages([message], [])
    assert len(pool) == 0


def test_file_index_none(text_file_info: TextFileInfo) -> None:
    message = HumanMessage.model_validate(
        {
            "contents": [
                {
                    "text": "Hello",
                    "files": [
                        text_file_info.as_metadata_only(),
                    ],
                },
            ]
        }
    )

    _, pool = hydrate_messages([message], [])
    assert len(pool) == 0


def test_not_metadata_only(text_file_info: TextFileInfo) -> None:
    message = HumanMessage.model_validate(
        {
            "contents": [
                {
                    "text": "Hello",
                    "files": [
                        text_file_info,
                    ],
                },
            ]
        }
    )

    _, pool = hydrate_messages([message], [text_file_info])
    assert len(pool) == 1
