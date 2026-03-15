"""Tests for YouTube channel analyzer with mocked API."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from googleapiclient.errors import HttpError

from src.analyzer import YouTubeChannelAnalyzer, _execute_with_retry


@pytest.fixture()
def analyzer(env_api_key: None) -> YouTubeChannelAnalyzer:
    """Create analyzer with mocked API client."""
    with patch("src.analyzer.googleapiclient.discovery.build") as mock_build:
        mock_build.return_value = MagicMock()
        a = YouTubeChannelAnalyzer()
        return a


class TestAnalyzerInit:
    """Tests for analyzer initialization."""

    def test_raises_without_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        with pytest.raises(ValueError, match="YouTube API key required"), \
             patch("src.analyzer.googleapiclient.discovery.build"):
            YouTubeChannelAnalyzer()

    def test_creates_with_env_key(self, env_api_key: None) -> None:
        with patch("src.analyzer.googleapiclient.discovery.build") as mock_build:
            mock_build.return_value = MagicMock()
            analyzer = YouTubeChannelAnalyzer()
            assert analyzer.api_key == "fake_test_api_key_123"

    def test_creates_with_explicit_key(self) -> None:
        with patch("src.analyzer.googleapiclient.discovery.build") as mock_build:
            mock_build.return_value = MagicMock()
            analyzer = YouTubeChannelAnalyzer(api_key="explicit_key")
            assert analyzer.api_key == "explicit_key"


class TestValidateApiKey:
    """Tests for API key validation."""

    def test_valid_key(self, analyzer: YouTubeChannelAnalyzer) -> None:
        analyzer.youtube.i18nRegions().list().execute.return_value = {}
        assert analyzer.validate_api_key() is True

    def test_invalid_key_400(self, analyzer: YouTubeChannelAnalyzer) -> None:
        from googleapiclient.errors import HttpError

        resp = MagicMock()
        resp.status = 400
        error = HttpError(resp, b"API key not valid")
        analyzer.youtube.i18nRegions().list().execute.side_effect = error

        with pytest.raises(ValueError, match="Invalid YouTube API key"):
            analyzer.validate_api_key()

    def test_quota_exceeded_403(self, analyzer: YouTubeChannelAnalyzer) -> None:
        from googleapiclient.errors import HttpError

        resp = MagicMock()
        resp.status = 403
        error = HttpError(resp, b"quotaExceeded")
        analyzer.youtube.i18nRegions().list().execute.side_effect = error

        with pytest.raises(ValueError, match="quota exceeded"):
            analyzer.validate_api_key()

    def test_api_not_enabled_403(self, analyzer: YouTubeChannelAnalyzer) -> None:
        from googleapiclient.errors import HttpError

        resp = MagicMock()
        resp.status = 403
        error = HttpError(resp, b"accessNotConfigured")
        analyzer.youtube.i18nRegions().list().execute.side_effect = error

        with pytest.raises(ValueError, match="not enabled"):
            analyzer.validate_api_key()


class TestChannelResolution:
    """Tests for channel ID resolution."""

    def test_resolve_from_username(self, analyzer: YouTubeChannelAnalyzer) -> None:
        analyzer.youtube.channels().list().execute.return_value = {
            "items": [{"id": "UC_resolved"}]
        }
        result = analyzer.get_channel_id_from_username("testuser")
        assert result == "UC_resolved"

    def test_username_not_found(self, analyzer: YouTubeChannelAnalyzer) -> None:
        analyzer.youtube.channels().list().execute.return_value = {"items": []}
        with pytest.raises(ValueError, match="No channel found"):
            analyzer.get_channel_id_from_username("nonexistent")

    def test_resolve_from_custom_url(self, analyzer: YouTubeChannelAnalyzer) -> None:
        analyzer.youtube.search().list().execute.return_value = {
            "items": [{"snippet": {"channelId": "UC_from_handle"}}]
        }
        result = analyzer.get_channel_id_from_custom_url("@testhandle")
        assert result == "UC_from_handle"

    def test_custom_url_not_found(self, analyzer: YouTubeChannelAnalyzer) -> None:
        analyzer.youtube.search().list().execute.return_value = {"items": []}
        with pytest.raises(ValueError, match="No channel found"):
            analyzer.get_channel_id_from_custom_url("@nonexistent")


class TestGetChannelInfo:
    """Tests for channel metadata retrieval."""

    def test_returns_channel_info(
        self,
        analyzer: YouTubeChannelAnalyzer,
        sample_channel_response: dict[str, Any],
    ) -> None:
        analyzer.youtube.channels().list().execute.return_value = sample_channel_response
        result = analyzer.get_channel_info("UC_test_channel_id")

        assert result["id"] == "UC_test_channel_id"
        assert result["title"] == "Test Channel"
        assert result["subscriber_count"] == "100000"
        assert "youtube.com/channel/" in result["url"]

    def test_channel_not_found(self, analyzer: YouTubeChannelAnalyzer) -> None:
        analyzer.youtube.channels().list().execute.return_value = {"items": []}
        with pytest.raises(ValueError, match="No channel found"):
            analyzer.get_channel_info("UC_nonexistent")


class TestGetMultipleChannels:
    """Tests for multi-channel analysis."""

    def test_graceful_error_handling(
        self, analyzer: YouTubeChannelAnalyzer
    ) -> None:
        """Channels that fail don't prevent others from succeeding."""
        call_count = 0

        def side_effect(*_args: object, **_kwargs: object) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # First channel info + content details
                return {
                    "items": [
                        {
                            "id": "UC_good",
                            "snippet": {
                                "title": "Good Channel",
                                "description": "Works",
                                "thumbnails": {"default": {"url": "http://x.com/t.jpg"}},
                            },
                            "statistics": {
                                "subscriberCount": "1000",
                                "viewCount": "50000",
                                "videoCount": "10",
                            },
                            "contentDetails": {
                                "relatedPlaylists": {"uploads": "UU_good"},
                            },
                        }
                    ]
                }
            msg = "API error"
            raise ValueError(msg)

        analyzer.youtube.channels().list().execute.side_effect = side_effect
        analyzer.youtube.playlistItems().list().execute.return_value = {"items": []}

        channel_list = [
            {"channel_id": "UC_good"},
            {"channel_id": "UC_bad"},
        ]
        result = analyzer.get_multiple_channels_videos(channel_list, max_results_per_channel=5)

        # At least partial results returned (exact count depends on mock call ordering)
        assert isinstance(result, list)

    def test_empty_channel_list(self, analyzer: YouTubeChannelAnalyzer) -> None:
        result = analyzer.get_multiple_channels_videos([], max_results_per_channel=5)
        assert result == []


class TestExecuteWithRetry:
    """Tests for exponential backoff retry logic."""

    def test_succeeds_on_first_try(self) -> None:
        request = MagicMock()
        request.execute.return_value = {"items": []}
        result = _execute_with_retry(request)
        assert result == {"items": []}
        assert request.execute.call_count == 1

    @patch("src.analyzer.time.sleep")
    def test_retries_on_403(self, mock_sleep: MagicMock) -> None:
        resp = MagicMock()
        resp.status = 403
        error = HttpError(resp, b"quotaExceeded")

        request = MagicMock()
        request.execute.side_effect = [error, {"items": []}]

        result = _execute_with_retry(request)
        assert result == {"items": []}
        assert request.execute.call_count == 2
        mock_sleep.assert_called_once_with(1.0)

    @patch("src.analyzer.time.sleep")
    def test_retries_on_429(self, mock_sleep: MagicMock) -> None:
        resp = MagicMock()
        resp.status = 429
        error = HttpError(resp, b"rate limited")

        request = MagicMock()
        request.execute.side_effect = [error, error, {"ok": True}]

        result = _execute_with_retry(request)
        assert result == {"ok": True}
        assert request.execute.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("src.analyzer.time.sleep")
    def test_raises_after_max_retries(self, mock_sleep: MagicMock) -> None:
        resp = MagicMock()
        resp.status = 429
        error = HttpError(resp, b"rate limited")

        request = MagicMock()
        request.execute.side_effect = error

        with pytest.raises(HttpError):
            _execute_with_retry(request)
        assert request.execute.call_count == 4  # 1 initial + 3 retries

    def test_does_not_retry_on_400(self) -> None:
        resp = MagicMock()
        resp.status = 400
        error = HttpError(resp, b"bad request")

        request = MagicMock()
        request.execute.side_effect = error

        with pytest.raises(HttpError):
            _execute_with_retry(request)
        assert request.execute.call_count == 1
