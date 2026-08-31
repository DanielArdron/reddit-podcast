from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree.ElementTree import fromstring

from app.config import Settings
from app.models import Comment, RedditPost
from app.service import PodcastService, script_for
from app.storage import EpisodeStore


class Reddit:
    def __init__(self, posts): self.posts = posts
    def top_posts(self, subreddit, after, before): return [p for p in self.posts if p.subreddit == subreddit]
    def fetch_comments(self, post, limit): return [Comment("a", "first"), Comment("b", "second"), Comment("c", "third")]


class TTS:
    def synthesize(self, text, output_path): output_path.write_bytes(b"wav")


class Audio:
    def __init__(self, duration=10): self.duration = duration
    def assemble(self, segments, output_path): output_path.write_bytes(b"mp3"); return self.duration


def post(id, subreddit, score, **kwargs):
    return RedditPost(id, subreddit, f"Title {id}", "author", "A story", f"https://reddit/{id}", score, datetime.now(timezone.utc), **kwargs)


def service(tmp_path, posts, duration=10):
    s = Settings(subreddits=("one", "two"), posts_per_subreddit=2, data_dir=str(tmp_path), audio_dir=str(tmp_path / "audio"), feed_url="https://host/redditfeed.xml")
    return PodcastService(s, Reddit(posts), TTS(), Audio(duration), EpisodeStore(tmp_path / "db.sqlite"))


def test_selects_top_posts_per_subreddit_and_filters(tmp_path):
    posts = [post(str(i), "one", i) for i in range(4)] + [post("link", "one", 99, is_self=False), post("nsfw", "two", 1, is_nsfw=True)]
    selected = service(tmp_path, posts).select_posts()
    assert [p.id for p in selected] == ["3", "2", "nsfw"]


def test_process_creates_one_episode_and_only_two_comments(tmp_path):
    svc = service(tmp_path, [post("x", "one", 10)])
    episodes = svc.process()
    assert len(episodes) == 1
    assert "Top comment 2" in episodes[0].description
    assert "Top comment 3" not in episodes[0].description
    assert episodes[0].audio_path.endswith("/audio/x.mp3")


def test_overlong_episode_is_skipped(tmp_path):
    svc = service(tmp_path, [post("x", "one", 10)], duration=1801)
    assert svc.process() == []
    assert svc.store.all() == []


def test_token_is_added_to_audio_url(tmp_path):
    s = Settings(subreddits=("one",), data_dir=str(tmp_path), audio_dir=str(tmp_path / "audio"), feed_url="https://host/redditfeed.xml", feed_token="secret")
    svc = PodcastService(s, Reddit([post("x", "one", 10)]), TTS(), Audio(), EpisodeStore(tmp_path / "db.sqlite"))
    assert svc.process()[0].audio_path.endswith("/audio/x.mp3?token=secret")


def test_feed_contains_episode(tmp_path):
    svc = service(tmp_path, [post("x", "one", 10)])
    svc.process()
    feed = svc.feed().decode()
    assert "r/one: Title x" in feed
    assert "audio/x.mp3" in feed
    fromstring(feed.encode())


def test_script_cleans_basic_markdown_and_links():
    p = post("x", "one", 1)
    assert script_for(p, [Comment("a", "**hello** https://example.test")]).endswith("hello")
