import os
from dataclasses import dataclass, field


DEFAULT_SUBREDDITS = (
    "BestofRedditorUpdates",
    "TalesFromTheFrontDesk",
    "talesfromtechsupport",
)


def _csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip().removeprefix("r/") for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    subreddits: tuple[str, ...] = DEFAULT_SUBREDDITS
    posts_per_subreddit: int = 6
    lookback_hours: int = 24
    comments_per_post: int = 2
    max_episode_seconds: int = 30 * 60
    run_time: str = "05:00"
    timezone: str = "Europe/London"
    data_dir: str = "./data"
    audio_dir: str = "./data/audio"
    feed_url: str = "https://podcasts.danielardron.co.uk/redditfeed.xml"
    feed_title: str = "Reddit Podcast"
    feed_description: str = "Personal narrated Reddit stories."
    feed_token: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "reddit-podcast/0.1 by personal-user"
    piper_executable: str = "piper"
    piper_model: str = ""
    ffmpeg_executable: str = "ffmpeg"

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()
        return cls(
            subreddits=_csv(os.getenv("SUBREDDITS", ",".join(defaults.subreddits))),
            posts_per_subreddit=int(os.getenv("POSTS_PER_SUBREDDIT", defaults.posts_per_subreddit)),
            lookback_hours=int(os.getenv("LOOKBACK_HOURS", defaults.lookback_hours)),
            comments_per_post=int(os.getenv("COMMENTS_PER_POST", defaults.comments_per_post)),
            max_episode_seconds=int(os.getenv("MAX_EPISODE_MINUTES", 30)) * 60,
            run_time=os.getenv("RUN_TIME", defaults.run_time),
            timezone=os.getenv("TIMEZONE", defaults.timezone),
            data_dir=os.getenv("DATA_DIR", defaults.data_dir),
            audio_dir=os.getenv("AUDIO_DIR", defaults.audio_dir),
            feed_url=os.getenv("FEED_URL", defaults.feed_url),
            feed_title=os.getenv("FEED_TITLE", defaults.feed_title),
            feed_description=os.getenv("FEED_DESCRIPTION", defaults.feed_description),
            feed_token=os.getenv("FEED_TOKEN", ""),
            reddit_client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            reddit_user_agent=os.getenv("REDDIT_USER_AGENT", defaults.reddit_user_agent),
            piper_executable=os.getenv("PIPER_EXECUTABLE", defaults.piper_executable),
            piper_model=os.getenv("PIPER_MODEL", defaults.piper_model),
            ffmpeg_executable=os.getenv("FFMPEG_EXECUTABLE", defaults.ffmpeg_executable),
        )
