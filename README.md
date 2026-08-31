# Reddit Podcast

A personal, self-hosted service that turns selected Reddit text posts into narrated podcast episodes.

## Initial configuration

- `r/BestofRedditorUpdates`
- `r/TalesFromTheFrontDesk`
- `r/talesfromtechsupport`
- Six highest-scoring eligible posts per subreddit every 24 hours
- One episode per post
- Original post plus the two highest-ranked comments
- NSFW posts allowed
- Deleted/removed, link, image, and video posts excluded
- Episodes longer than 30 minutes skipped
- Daily run at 05:00 Europe/London
- Local Piper text-to-speech

See [DEPLOYMENT.md](DEPLOYMENT.md) for OpenMediaVault, Docker Compose, GitHub Container Registry, and Cloudflare Tunnel setup.
