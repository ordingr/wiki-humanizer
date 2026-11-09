#!/usr/bin/env python3
"""Fetch Wikipedia articles as they stood before ChatGPT launched (30 Nov 2022).

Any revision saved before that date was written by people, so the saved
text is a safe reference sample of human encyclopedic prose.

Usage:
    python fetch_human_corpus.py                      # default article list
    python fetch_human_corpus.py "Toyota" "Sushi"     # your own titles
    python fetch_human_corpus.py --date 2021-06-01    # earlier cut-off

Writes one .txt per article plus manifest.json to references/human-corpus/.
Standard library only.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

API = "https://en.wikipedia.org/w/api.php"
UA = "wiki-humanizer/1.0 (personal writing-style corpus; low volume)"
CHATGPT_LAUNCH = "2022-11-30"
OUT = Path(__file__).resolve().parent.parent / "references" / "human-corpus"

# Mix of science, history, business, tech, places and people, so the corpus
# covers the kinds of things the user actually writes about.
DEFAULT_TITLES = [
    "Sun", "Photosynthesis", "Tuberculosis", "Plate tectonics",
    "Byzantine Empire", "Industrial Revolution", "Ada Lovelace", "Alan Turing",
    "Toyota Production System", "Shipping container", "Supply chain management",
    "Warehouse", "Cloud computing", "SQL", "Python (programming language)",
    "Microsoft Excel", "Toronto", "Coffee",
]


def api(params, tries=5):
    params = {**params, "format": "json", "formatversion": "2", "maxlag": 5}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": UA})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            # Wikipedia throttles anonymous parse calls; wait as told, or back off.
            wait = int(e.headers.get("Retry-After") or 0) or 10 * 2 ** attempt
            print(f"       rate limited, waiting {wait}s")
            time.sleep(wait)


def revision_before(title, date):
    data = api({"action": "query", "prop": "revisions", "titles": title,
                "rvlimit": 1, "rvdir": "older", "rvstart": date + "T00:00:00Z",
                "rvprop": "ids|timestamp", "redirects": 1})
    page = data["query"]["pages"][0]
    if page.get("missing") or "revisions" not in page:
        return None
    rev = page["revisions"][0]
    return page["title"], rev["revid"], rev["timestamp"]


class ParagraphText(HTMLParser):
    """Collects text from <p> tags, skipping citation markers and styles."""
    SKIP = {"sup", "style", "script", "table"}

    def __init__(self):
        super().__init__()
        self.paras, self.buf, self.in_p, self.skip = [], [], 0, 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "p":
            self.in_p += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == "p" and self.in_p:
            self.in_p -= 1
            text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if len(text.split()) >= 12:  # drop stubs and coordinates lines
                self.paras.append(text)
            self.buf = []

    def handle_data(self, data):
        if self.in_p and not self.skip:
            self.buf.append(data)


def article_text(revid):
    html = api({"action": "parse", "oldid": revid, "prop": "text",
                "disablelimitreport": 1})["parse"]["text"]
    p = ParagraphText()
    p.feed(html)
    return "\n\n".join(p.paras)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("titles", nargs="*", help="article titles (default: built-in list)")
    ap.add_argument("--date", default="2022-11-01",
                    help="take the last revision before this date (YYYY-MM-DD)")
    args = ap.parse_args()
    if args.date >= CHATGPT_LAUNCH:
        sys.exit(f"--date must be before {CHATGPT_LAUNCH} to guarantee human text")

    OUT.mkdir(parents=True, exist_ok=True)
    for title in args.titles or DEFAULT_TITLES:
        try:
            found = revision_before(title, args.date)
            if not found:
                print(f"skip   {title}: no revision before {args.date}")
                continue
            real_title, revid, ts = found
            text = article_text(revid)
        except Exception as e:  # keep going; one bad title shouldn't stop the run
            print(f"error  {title}: {e}")
            continue
        fname = re.sub(r"[^\w\-]+", "_", real_title).strip("_") + ".txt"
        url = f"https://en.wikipedia.org/w/index.php?oldid={revid}"
        (OUT / fname).write_text(f"# {real_title}\n# revision {revid}, saved {ts}\n# {url}\n\n{text}\n", "utf-8")
        manifest = write_manifest()
        print(f"saved  {real_title}  rev {revid} ({ts[:10]})  {len(text.split())} words")
        time.sleep(3)

    manifest = write_manifest()
    print(f"\n{len(manifest)} articles in {OUT}")


def write_manifest():
    """Rebuild manifest.json from the corpus file headers.

    The files are the source of truth, so runs that overlap can't drop
    each other's entries the way a read-at-start, write-at-end merge did.
    """
    manifest = {}
    for f in sorted(OUT.glob("*.txt")):
        head = f.read_text("utf-8").split("\n\n", 1)
        m = re.match(r"# (.+)\n# revision (\d+), saved (\S+)\n# (\S+)", head[0])
        if not m:
            continue
        title, revid, ts, url = m.groups()
        manifest[title] = {"file": f.name, "revid": int(revid), "timestamp": ts,
                           "url": url, "words": len(head[1].split()) if len(head) > 1 else 0}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), "utf-8")
    return manifest


if __name__ == "__main__":
    main()
