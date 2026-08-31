import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence
from urllib.parse import urlencode

from .config import Settings
from .models import Comment, Episode, RedditPost
from .providers import AudioAssembler, RedditProvider, TTSProvider
from .rss import render_feed
from .storage import EpisodeStore


def clean_text(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_~`]", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def script_for(post: RedditPost, comments: Sequence[Comment]) -> str:
    parts = [f"From the subreddit {post.subreddit}. {post.title}.", f"Posted by {post.author}.", clean_text(post.body)]
    for index, comment in enumerate(comments, 1):
        parts.append(f"Top comment {index}, by {comment.author}. {clean_text(comment.body)}")
    return "\n\n".join(p for p in parts if p)


class PodcastService:
    def __init__(self, settings: Settings, reddit: RedditProvider, tts: TTSProvider, audio: AudioAssembler, store: EpisodeStore):
        self.settings, self.reddit, self.tts, self.audio, self.store = settings, reddit, tts, audio, store
        Path(settings.audio_dir).mkdir(parents=True, exist_ok=True)

    def eligible(self, post: RedditPost) -> bool:
        return post.is_self and not post.is_video and not post.is_image and not post.removed and bool(post.body.strip())

    def select_posts(self, now: datetime | None = None) -> list[RedditPost]:
        now = now or datetime.now(timezone.utc)
        after = now - timedelta(hours=self.settings.lookback_hours)
        selected: list[RedditPost] = []
        for subreddit in self.settings.subreddits:
            posts = [p for p in self.reddit.top_posts(subreddit, after, now) if self.eligible(p) and not self.store.exists(p.id)]
            selected.extend(sorted(posts, key=lambda p: p.score, reverse=True)[: self.settings.posts_per_subreddit])
        return selected

    def process(self, now: datetime | None = None) -> list[Episode]:
        episodes = []
        for post in self.select_posts(now):
            comments = self.reddit.fetch_comments(post, self.settings.comments_per_post)[: self.settings.comments_per_post]
            script = script_for(post, comments)
            segment = Path(self.settings.audio_dir) / f"{post.id}.wav"
            output = Path(self.settings.audio_dir) / f"{post.id}.mp3"
            self.tts.synthesize(script, segment)
            duration = self.audio.assemble([segment], output)
            if duration > self.settings.max_episode_seconds:
                output.unlink(missing_ok=True)
                segment.unlink(missing_ok=True)
                continue
            audio_url = f"{self.settings.feed_url.rsplit('/', 1)[0]}/audio/{output.name}"
            if self.settings.feed_token:
                audio_url += "?" + urlencode({"token": self.settings.feed_token})
            episode = Episode(post.id, f"r/{post.subreddit}: {post.title}", post.subreddit, post.permalink, post.author, post.created_at, duration, audio_url, script)
            self.store.add(episode)
            segment.unlink(missing_ok=True)
            episodes.append(episode)
        return episodes

    def feed(self) -> bytes:
        return render_feed(self.settings, self.store.all())
