---
title: Getting Started
description: Install youtube-toolkit, configure your API key, define channels, and run your first analysis.
---

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Runtime |
| Poetry | latest | Dependency management |
| Task (go-task) | v3 | Task runner (`Taskfile.yml`) |
| YouTube Data API v3 key | — | Channel and video data |

Get an API key from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials). Enable the **YouTube Data API v3** for the project associated with that key.

## Install

```bash
git clone https://github.com/mlorentedev/youtube-toolkit.git
cd youtube-toolkit
task install
```

`task install` runs `poetry install --sync --no-root` inside an in-project virtualenv.

## Configure

### Environment variables

Create a `.env` file in the project root:

```ini
# Required
YOUTUBE_API_KEY=your-api-key-here

# Optional
MAX_RESULTS_PER_CHANNEL=100   # Videos fetched per channel (default: 50)
OUTPUT_DIR=./output            # Report output directory (default: ./output)
VIDEO_ID=dQw4w9WgXcQ           # Default video ID for transcript mode
```

The API key is validated before every run. If it is missing, expired, or over quota, you get a descriptive error with a link to the console.

### Channel list

Create a `channels.yml` file in the project root. Each entry needs exactly one identifier:

```yaml
# By @handle (most common)
- custom_url: "@technotim"
- custom_url: "@christianlempa"

# By legacy username
- username: "GoogleDevelopers"

# By raw channel ID
- channel_id: "UCxxxxxxxxxxxxxx"
```

## Run

### Analyze channels

```bash
task run:channels
```

This fetches videos from every channel in `channels.yml` (up to `MAX_RESULTS_PER_CHANNEL` per channel), computes engagement metrics, and writes a timestamped report folder under `output/`. Each batch request retrieves statistics for 50 videos at a time to stay within API limits.

**Generated files per run:**

| File | Format | Contents |
|---|---|---|
| `youtube_channels_videos_<ts>.csv` | CSV | All videos with 15 columns: channel, subscribers, title, date, URL, views, likes, comments, duration, and 6 calculated metrics |
| `youtube_channel_stats_<ts>.txt` | TXT | Per-channel breakdown: metadata, upload frequency, averages, top 5 by views, top 5 by engagement, performance distribution |
| `youtube_engagement_trends_<ts>.txt` | TXT | Cross-channel rankings by engagement and view rate, content performance by duration category (short < 5 min, medium 5-15 min, long > 15 min), top 10 engagement, top 5 viral |
| `youtube_best_videos_<ts>.txt` | URL list | Top 15 videos per channel by engagement rate, one URL per line |
| `youtube_latest_videos_<ts>.txt` | URL list | 15 most recent videos per channel, one URL per line |
| `README.md` | Markdown | Self-documenting index explaining every file in the folder |

### Download a transcript

```bash
task run:video

# Or specify a video ID and languages directly
poetry run python -m src.main video dQw4w9WgXcQ --langs en,es
```

The downloader tries your preferred languages first, falls back to the first available transcript, and finally checks a local fixtures directory (`YOUTUBE_TRANSCRIPT_FIXTURES_DIR`) for offline use.

Output: `<video_id>_transcript.txt` in the output directory.

## Engagement metrics reference

Every video in the CSV and reports includes these computed fields:

| Metric | Formula | Interpretation |
|---|---|---|
| Engagement Rate (Views) | `(likes + comments) / views * 100` | Audience interaction relative to reach |
| Engagement Rate (Subscribers) | `(likes + comments) / subscribers * 100` | Interaction relative to channel size |
| View Rate | `views / subscribers * 100` | Viral signal when above 100% |
| Like Rate | `likes / views * 100` | Content satisfaction |
| Comment Rate | `comments / views * 100` | Discussion intensity |
| Views per Minute | `views / (duration_seconds / 60)` | Content efficiency — higher means more views per unit of content |
