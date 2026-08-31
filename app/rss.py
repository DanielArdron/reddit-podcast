from datetime import timezone
from email.utils import format_datetime
from xml.etree.ElementTree import Element, SubElement, tostring

from .config import Settings
from .models import Episode


def render_feed(settings: Settings, episodes: list[Episode]) -> bytes:
    rss = Element("rss", {"version": "2.0", "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"})
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = settings.feed_title
    SubElement(channel, "link").text = settings.feed_url
    SubElement(channel, "description").text = settings.feed_description
    for episode in episodes:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = episode.title
        SubElement(item, "guid", {"isPermaLink": "false"}).text = episode.id
        SubElement(item, "link").text = episode.post_url
        SubElement(item, "description").text = episode.description
        published = episode.published_at.astimezone(timezone.utc)
        SubElement(item, "pubDate").text = format_datetime(published)
        SubElement(item, "itunes:duration").text = str(episode.duration_seconds)
        SubElement(item, "enclosure", {"url": episode.audio_path, "type": "audio/mpeg", "length": "0"})
    return tostring(rss, encoding="utf-8", xml_declaration=True)
