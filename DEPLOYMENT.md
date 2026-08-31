# Reddit Podcast deployment

This repository contains the Docker packaging for a personal Reddit-to-podcast service. It is intended for OpenMediaVault's Docker Compose UI and an existing Cloudflare Tunnel.

The application image is published by GitHub Actions to:

```text
ghcr.io/danielardron/reddit-podcast:latest
```

## Before deploying

1. Confirm that the GitHub Actions workflow has published the image from the `main` branch.
2. Wait for the **Publish Docker image** workflow to complete.
3. If the package is private, authenticate the OMV Docker host to GHCR. A public repository/package avoids that extra step.
4. Create two OMV shared folders, one for application state and one for generated MP3 episodes.
5. Copy `.env.example` to `.env` in the OMV Compose project directory.
6. Replace `GHCR_IMAGE`, both OMV paths, the Reddit credentials, and `FEED_TOKEN`.

The committed files contain placeholders only. Keep `.env` private and do not commit it.

## Reddit API setup

Create a Reddit OAuth application for personal/script use and put its client ID and secret in `.env`. The user agent should identify this service and your Reddit username. The service should use OAuth and respect Reddit's rate limits.

## OMV Compose UI

Paste `compose.yaml` into the Compose project, or upload it if the OMV interface supports file upload. Put `.env` beside it. Update the two host paths to real absolute paths, for example paths under your OMV appdata share and an episodes share.

The container exposes its RSS web service on port 8080. The host-side port is controlled by `RSS_PORT`.

Persistent mounts:

| Container path | Purpose |
|---|---|
| `/data` | SQLite/database state, feed metadata, and application configuration |
| `/episodes` | Generated MP3 files served by the RSS feed |

The container restarts automatically and reports healthy when `GET /health` returns successfully.

## Application configuration contract

The later application implementation should read these environment variables:

- `TIMEZONE=Europe/London`
- `RUN_TIME=05:00`
- `SUBREDDITS=BestofRedditorUpdates,TalesFromTheFrontDesk,talesfromtechsupport`
- `POSTS_PER_SUBREDDIT=6`
- `COMMENTS_PER_POST=2`
- `MAX_EPISODE_MINUTES=30`
- `LOOKBACK_HOURS=24`
- `PIPER_MODEL=/data/models/en_GB-alan-medium.onnx`

The intended result is up to six eligible text posts per subreddit per daily run, with one podcast episode per post. The original post and its two highest-ranked comments should be read. NSFW posts are allowed; deleted/removed posts and non-text link, image, or video posts are excluded. Posts expected to exceed 30 minutes should be skipped.

## Cloudflare Tunnel

Route the existing tunnel hostname to the host port selected by `RSS_PORT`:

```text
https://podcasts.danielardron.co.uk/redditfeed.xml
```

The Compose file sets this as `FEED_URL` so the generated RSS enclosure URLs can be correct. The application must serve the feed at that path and serve episode files below the same public base path. If the tunnel maps the hostname directly to port 8080, leave `RSS_PORT=8080`.

Use HTTPS and keep the feed token private. Podcast applications commonly handle a tokenized feed URL more reliably than an interactive Cloudflare Access login. The exact feed URL format is an application concern, but it should include the configured `FEED_TOKEN` or an equivalent unguessable path/query token.

## Updating

Push to `main` to publish a new `latest` image. In OMV, pull/recreate the Compose project to deploy it. For a pinned deployment, set `IMAGE_TAG` to a version tag such as `v0.1.0`; the workflow also publishes immutable SHA tags.

## Piper voice model

The image installs Piper but does not bake a voice model into the image. Download an English Piper `.onnx` voice and its matching `.onnx.json` file, place them under the persistent appdata directory, and set `PIPER_MODEL` to the container path. The model is retained across image updates.
