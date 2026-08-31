from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Comment:
    author: str
    body: str
    score: int = 0


@dataclass(frozen=True)
class RedditPost:
    id: str
    subreddit: str
    title: str
    author: str
    body: str
    permalink: str
    score: int
    created_at: datetime
    is_self: bool = True
    is_video: bool = False
    is_image: bool = False
    is_nsfw: bool = False
    removed: bool = False
    comments: tuple[Comment, ...] = ()


@dataclass(frozen=True)
class Episode:
    id: str
    title: str
    subreddit: str
    post_url: str
    author: str
    published_at: datetime
    duration_seconds: int
    audio_path: str
    description: str
