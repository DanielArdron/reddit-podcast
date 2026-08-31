import argparse
from pathlib import Path

from .api import serve
from .config import Settings
from .providers import FfmpegAssembler, PiperTTS, RedditAPI
from .service import PodcastService
from .storage import EpisodeStore


def build_service(settings: Settings) -> PodcastService:
    return PodcastService(settings, RedditAPI(settings.reddit_client_id, settings.reddit_client_secret, settings.reddit_user_agent), PiperTTS(settings.piper_executable, settings.piper_model), FfmpegAssembler(settings.ffmpeg_executable), EpisodeStore(Path(settings.data_dir) / "episodes.sqlite3"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "serve"))
    args = parser.parse_args()
    settings = Settings.from_env()
    service = build_service(settings)
    if args.command == "run":
        service.process()
    else:
        serve(service, port=int(__import__("os").getenv("PORT", "8080")), feed_token=settings.feed_token)
