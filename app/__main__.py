"""Daily scheduler entry point for the container."""

import time
from datetime import datetime
from threading import Thread
from zoneinfo import ZoneInfo

from .api import serve
from .cli import build_service
from .config import Settings


def main() -> None:
    settings = Settings.from_env()
    service = build_service(settings)
    Thread(
        target=serve,
        kwargs={"service": service, "port": int(__import__("os").getenv("PORT", "8080")), "feed_token": settings.feed_token},
        daemon=True,
    ).start()
    timezone = ZoneInfo(settings.timezone)
    last_run_date = None
    while True:
        now = datetime.now(timezone)
        if now.strftime("%H:%M") == settings.run_time and last_run_date != now.date():
            service.process(now.astimezone())
            last_run_date = now.date()
        time.sleep(20)


if __name__ == "__main__":
    main()
