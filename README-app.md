# reddit-podcast application core

This directory contains the Python core for a private daily podcast generated from Reddit text posts. It intentionally does not include Docker, Compose, or GitHub workflow files.

## Behaviour

At each run, the service checks the previous 24 hours and selects the six highest-scoring eligible text posts from each configured subreddit. It does not exclude NSFW posts. It skips non-self posts, deleted/removed posts, and image/video posts, fetches the top two comments, creates one episode per post, and skips audio longer than 30 minutes.

Defaults are `r/BestofRedditorUpdates`, `r/TalesFromTheFrontDesk`, and `r/talesfromtechsupport`, with a 05:00 run-time setting. Configuration is via environment variables; credentials are never stored in source.

## Local commands

```bash
pip install -e '.[test]'
pytest
reddit-podcast run
reddit-podcast serve
```

The HTTP server serves `/redditfeed.xml` and `/audio/<filename>`. Set `FEED_TOKEN` to require `/redditfeed.xml?token=<value>` and to add the token to enclosure URLs. The configured `FEED_URL` defaults to `https://podcasts.danielardron.co.uk/redditfeed.xml`.

Useful variables include `SUBREDDITS`, `POSTS_PER_SUBREDDIT`, `LOOKBACK_HOURS`, `COMMENTS_PER_POST`, `MAX_EPISODE_MINUTES`, `DATA_DIR`, `AUDIO_DIR`, `FEED_URL`, `FEED_TOKEN`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`, `PIPER_MODEL`, `PIPER_EXECUTABLE`, `FFMPEG_EXECUTABLE`, and `PORT`.

## Provider boundaries

`RedditAPI`, `PiperTTS`, and `FfmpegAssembler` are production adapters. `PodcastService` accepts provider protocols, so tests or future adapters can inject mocked Reddit, TTS, and audio implementations.
