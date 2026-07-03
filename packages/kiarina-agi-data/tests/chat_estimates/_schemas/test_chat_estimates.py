from kiarina.agi.chat_estimates import ChatEstimates


def test_chat_estimates() -> None:
    estimates = ChatEstimates(
        file_size=12345,
        text_file_count=2,
        text_token_count=100,
        image_file_count=1,
        image_token_count=200,
        audio_file_count=1,
        audio_token_count=300,
        audio_duration=60.0,
        video_file_count=1,
        video_token_count=400,
        video_duration=120.0,
        pdf_file_count=1,
        pdf_token_count=500,
        pdf_page_count=10,
    )

    estimates.add_token_count("text", 100)
    estimates.add_token_count("image", 200)
    estimates.add_token_count("audio", 300)
    estimates.add_token_count("video", 400)
    estimates.add_token_count("pdf", 500)

    print(str(estimates))

    estimates_2 = estimates + estimates.model_copy(deep=True)

    print(str(estimates_2))
