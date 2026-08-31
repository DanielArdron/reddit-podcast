from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .service import PodcastService


def handler_for(service: PodcastService, feed_token: str = ""):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                body = b"ok\n"
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if feed_token and parse_qs(parsed.query).get("token", [""])[0] != feed_token:
                self.send_error(404)
                return
            if parsed.path == "/redditfeed.xml":
                body = service.feed()
                self.send_response(200); self.send_header("Content-Type", "application/rss+xml"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            if parsed.path.startswith("/audio/"):
                file = Path(service.settings.audio_dir) / Path(parsed.path.removeprefix("/audio/")).name
                if file.is_file():
                    body = file.read_bytes(); self.send_response(200); self.send_header("Content-Type", "audio/mpeg"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            self.send_error(404)
        def log_message(self, *_): pass
    return Handler


def serve(service: PodcastService, host: str = "0.0.0.0", port: int = 8080, feed_token: str = "") -> None:
    ThreadingHTTPServer((host, port), handler_for(service, feed_token)).serve_forever()
