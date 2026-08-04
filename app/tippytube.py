"""Tippy Tube video helper for the landing page.

Fetches the latest videos from the Tippy Tube YouTube channel via its public
RSS feed, caches them in-process, and falls back to a built-in snapshot if the
feed is ever slow or unreachable — so the landing page stays fast and never
breaks on an external dependency.
"""

import random
import time
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError

# Tippy Tube channel (youtube.com/@tippytube2340).
CHANNEL_ID = "UCjc_Y8l3kx8z4hA58ctjQuA"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

_NS = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}

# Snapshot of the channel used only when the live feed can't be reached.
SEED_VIDEOS = [
    {"id": "SFB2qOWCwk4", "title": "INC4802: Teaching Strategies For Inclusive Education by Dr Maite Maebana."},
    {"id": "0oCriupPXwY", "title": "Sunnyside Micro-Teaching Lesson: 2026"},
    {"id": "06d3hqy_rd0", "title": "What are Micro-Teaching Lessons? PURPOSE AND HOW TO BOOK!"},
    {"id": "QG5TJnIYqlk", "title": "Official Graduation: Instructional Leadership in Curriculum Delivery in Schools (25 April 2026)"},
    {"id": "J4fv8cEFTII", "title": "Critical Reflection on Teaching Practices For The Integration in Inclusive Settings:"},
    {"id": "7jj_xReIpfI", "title": "HSN1501: Health, Nutrition and Safety module presented by Dr MP Maloka"},
    {"id": "3kW-l5oqszE", "title": "Introduction to Emergent Mathematics Lesson 4"},
    {"id": "BNRBfEUAsW4", "title": "Introduction to Emergent Mathematics Presented by Mrs Pillay"},
    {"id": "pthnW4d38yE", "title": "Dr MP MALOKA gives a module lesson video for the module LSK2601."},
    {"id": "uEPqrGHTuRg", "title": "Introduction to Strategies to Teach Learners with Diverse Needs by Dr Lindokuhle Mkhuma"},
    {"id": "zpf4LztoGn0", "title": "Understand Learner Variabilty Using Theoretical Frameworks: Lesson by Dr Maebana."},
    {"id": "0_R9YMfu8o8", "title": "INC4808 with Dr Israel Lindokuhle Mkhuma"},
    {"id": "ug-9kh6F54c", "title": "Basic Number Sense Dr TJ Mampane"},
    {"id": "Hu0gJOAyQDE", "title": "FMT3701 Lesson 5 Dr TJ Mampane"},
    {"id": "gYUIjD3BxVQ", "title": "Micro-teaching Student Orientation 2026"},
]

_CACHE = {"videos": None, "fetched_at": 0.0}
_TTL_SECONDS = 6 * 3600
_TIMEOUT_SECONDS = 3


def _fetch_live():
    """Return the channel's videos from the live RSS feed, or None on failure."""
    try:
        with urlopen(FEED_URL, timeout=_TIMEOUT_SECONDS) as response:
            root = ET.parse(response).getroot()
    except (URLError, ET.ParseError, OSError):
        return None

    videos = []
    for entry in root.findall("a:entry", _NS):
        vid = entry.find("yt:videoId", _NS)
        title = entry.find("a:title", _NS)
        if vid is not None and vid.text and title is not None and title.text:
            videos.append({"id": vid.text, "title": title.text})
    return videos or None


def get_videos():
    """All known Tippy Tube videos, refreshed from the live feed at most every TTL."""
    now = time.time()
    if _CACHE["videos"] is None or now - _CACHE["fetched_at"] > _TTL_SECONDS:
        live = _fetch_live()
        if live:
            _CACHE["videos"] = live
            _CACHE["fetched_at"] = now
    return _CACHE["videos"] or SEED_VIDEOS


def pick_featured(count=6):
    """A random selection of videos for the landing page, each with a thumbnail URL."""
    pool = get_videos()
    chosen = random.sample(pool, min(count, len(pool)))
    return [
        {
            "id": v["id"],
            "title": v["title"],
            "url": f"https://www.youtube.com/watch?v={v['id']}",
            "thumbnail": f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg",
        }
        for v in chosen
    ]
