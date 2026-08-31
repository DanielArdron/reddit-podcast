import sqlite3
from threading import RLock
from datetime import datetime, timezone
from pathlib import Path

from .models import Episode


class EpisodeStore:
    def __init__(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = RLock()
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE TABLE IF NOT EXISTS episodes (id TEXT PRIMARY KEY, title TEXT, subreddit TEXT, post_url TEXT, author TEXT, published_at TEXT, duration_seconds INTEGER, audio_path TEXT, description TEXT)")
        self.db.commit()

    def exists(self, post_id: str) -> bool:
        with self.lock:
            return self.db.execute("SELECT 1 FROM episodes WHERE id=?", (post_id,)).fetchone() is not None

    def add(self, episode: Episode) -> None:
        with self.lock:
            self.db.execute("INSERT OR REPLACE INTO episodes VALUES (?,?,?,?,?,?,?,?,?)", (episode.id, episode.title, episode.subreddit, episode.post_url, episode.author, episode.published_at.isoformat(), episode.duration_seconds, episode.audio_path, episode.description))
            self.db.commit()

    def all(self) -> list[Episode]:
        with self.lock:
            rows = self.db.execute("SELECT * FROM episodes ORDER BY published_at DESC").fetchall()
        return [Episode(r["id"], r["title"], r["subreddit"], r["post_url"], r["author"], datetime.fromisoformat(r["published_at"]), r["duration_seconds"], r["audio_path"], r["description"]) for r in rows]
