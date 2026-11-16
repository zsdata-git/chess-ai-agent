from unittest.mock import MagicMock

import pytest

from backend.app.services import youtube_service


def test_empty_opening():

    result = youtube_service.search_youtube_videos(
        opening=""
    )

    assert result == []


def test_missing_api_key(monkeypatch):

    monkeypatch.delenv(
        "YOUTUBE_API_KEY",
        raising=False,
    )

    with pytest.raises(
        youtube_service.YouTubeServiceError
    ):
        youtube_service.search_youtube_videos(
            opening="Italian Game"
        )


def test_invalid_max_results():

    with pytest.raises(ValueError):
        youtube_service.search_youtube_videos(
            opening="Italian Game",
            max_results=20,
        )


def test_youtube_search(monkeypatch):

    monkeypatch.setenv(
        "YOUTUBE_API_KEY",
        "fake-test-key",
    )

    fake_response = {
        "items": [
            {
                "id": {
                    "videoId": "abc123"
                },
                "snippet": {
                    "title": "Italian Game Tutorial",
                    "description": "Chess lesson",
                    "channelTitle": "Chess Academy",
                    "publishedAt": "2026-01-01T00:00:00Z",
                    "thumbnails": {
                        "medium": {
                            "url": "https://example.com/image.jpg"
                        }
                    },
                },
            }
        ]
    }

    fake_youtube = MagicMock()

    fake_youtube.search.return_value.list.return_value.execute.return_value = (
        fake_response
    )

    monkeypatch.setattr(
        youtube_service,
        "build",
        lambda *args, **kwargs: fake_youtube,
    )

    videos = youtube_service.search_youtube_videos(
        opening="Italian Game"
    )

    assert len(videos) == 1

    assert videos[0]["video_id"] == "abc123"

    assert videos[0]["title"] == (
        "Italian Game Tutorial"
    )

    assert videos[0]["url"] == (
        "https://www.youtube.com/watch?v=abc123"
    )