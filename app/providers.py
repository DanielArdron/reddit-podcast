import base64
import json
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol, Sequence

from .models import Comment, RedditPost


class RedditProvider(Protocol):
    def top_posts(self, subreddit: str, after: datetime, before: datetime) -> Sequence[RedditPost]: ...
    def fetch_comments(self, post: RedditPost, limit: int) -> Sequence[Comment]: ...


class TTSProvider(Protocol):
    def synthesize(self, text: str, output_path: Path) -> None: ...


class AudioAssembler(Protocol):
    def assemble(self, segments: Sequence[Path], output_path: Path) -> int: ...


class RedditAPI(RedditProvider):
    """Small Reddit OAuth client. It deliberately exposes only the calls the app needs."""

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.client_id, self.client_secret, self.user_agent = client_id, client_secret, user_agent
        self._token: str | None = None

    def _request(self, url: str, *, data: bytes | None = None, auth: str | None = None) -> dict:
        headers = {"User-Agent": self.user_agent}
        if auth:
            headers["Authorization"] = f"Bearer {auth}"
        request = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    def _access_token(self) -> str:
        if self._token:
            return self._token
        credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        request = urllib.request.Request(
            "https://www.reddit.com/api/v1/access_token",
            data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
            headers={"Authorization": f"Basic {credentials}", "User-Agent": self.user_agent},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            self._token = json.load(response)["access_token"]
        return self._token

    @staticmethod
    def _post(item: dict) -> RedditPost:
        d = item["data"]
        created = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)
        return RedditPost(
            id=d["id"], subreddit=d["subreddit"], title=d.get("title", ""),
            author=d.get("author") or "[deleted]", body=d.get("selftext") or "",
            permalink="https://www.reddit.com" + d.get("permalink", ""), score=d.get("score", 0),
            created_at=created, is_self=d.get("is_self", False), is_video=d.get("is_video", False),
            is_image=(d.get("post_hint") == "image"), is_nsfw=d.get("over_18", False),
            removed=(d.get("selftext") or "").strip().lower() in {"[removed]", "[deleted]"},
        )

    def top_posts(self, subreddit: str, after: datetime, before: datetime) -> Sequence[RedditPost]:
        params = urllib.parse.urlencode({"t": "day", "limit": 100, "raw_json": 1})
        payload = self._request(f"https://oauth.reddit.com/r/{subreddit}/top?{params}", auth=self._access_token())
        posts = [self._post(x) for x in payload["data"]["children"]]
        return [p for p in posts if after <= p.created_at <= before]

    def fetch_comments(self, post: RedditPost, limit: int) -> Sequence[Comment]:
        url = f"https://oauth.reddit.com/comments/{post.id}?sort=top&limit={limit}&raw_json=1"
        payload = self._request(url, auth=self._access_token())
        children = payload[1]["data"]["children"]
        return [Comment(c["data"].get("author") or "[deleted]", c["data"].get("body") or "", c["data"].get("score", 0))
                for c in children if c.get("kind") == "t1" and c["data"].get("body")]


class PiperTTS(TTSProvider):
    def __init__(self, executable: str = "piper", model: str = ""):
        self.executable, self.model = executable, model

    def synthesize(self, text: str, output_path: Path) -> None:
        command = [self.executable, "--output_file", str(output_path)]
        if self.model:
            command += ["--model", self.model]
        subprocess.run(command, input=text.encode(), check=True)


class FfmpegAssembler(AudioAssembler):
    def __init__(self, executable: str = "ffmpeg"):
        self.executable = executable

    def assemble(self, segments: Sequence[Path], output_path: Path) -> int:
        concat = output_path.with_suffix(".concat.txt")
        concat.write_text("".join(f"file '{p.resolve()}'\n" for p in segments), encoding="utf-8")
        try:
            subprocess.run([self.executable, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-codec:a", "libmp3lame", "-b:a", "64k", str(output_path)], check=True)
            probe = subprocess.run([self.executable, "-i", str(output_path)], capture_output=True, text=True)
            import re
            match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
            return int(float(match.group(1)) * 3600 + float(match.group(2)) * 60 + float(match.group(3))) if match else 0
        finally:
            concat.unlink(missing_ok=True)
