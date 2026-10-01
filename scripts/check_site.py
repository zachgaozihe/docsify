#!/usr/bin/env python3
"""Offline checks for the personal Docsify site; no third-party packages needed."""

from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import os
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CONTENT = (
    "ai_map.md", "ai.md", "mit_AI.md", "4039DIS.md", "SaN.md",
    "diffusion.md", "networks_1.md", "networks_2.md",
)
ENGLISH_PAGES = ("README.md", "_sidebar.md", "_navbar.md", "src/inc/404.md") + CONTENT
CHINESE_PAGES = tuple("zh-cn/" + name for name in ("README.md", "_sidebar.md", "_navbar.md", "404.md") + CONTENT)
PAGES = ENGLISH_PAGES + CHINESE_PAGES
FULL_VERSION = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")
SENSITIVE = re.compile(
    r"(?:[\"']?\bsesskey\b[\"']?\s*(?:=|:|%3[dD])"
    r"|(?:name|id)\s*=\s*[\"']sesskey[\"']"
    r"|\bjoin-team-code\b\s*(?:=|:|/|%2[fF]|%3[dD]))",
    re.IGNORECASE,
)


def read(path):
    return path.read_text(encoding="utf-8-sig")


def without_examples(text):
    """Ignore comments, fenced blocks and inline code when checking page links."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    kept, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence is not None:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker[1]
        else:
            kept.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(kept))


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.scripts = []
        self.in_script = False
        self.script_text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.urls.extend(value for key, value in attrs if key in ("src", "href") and value)
        if tag == "script":
            self.in_script = True
            if attributes.get("src"):
                self.scripts.append(attributes["src"])

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.script_text.append(data)


def markdown_urls(text):
    # Inline and reference-style links/images. Titles and Docsify directives are ignored.
    urls = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)", text)
    urls.extend(re.findall(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.MULTILINE))
    parser = References()
    parser.feed(text)
    return urls + parser.urls


def local_target(url, source):
    url = unescape(url.strip().strip("<>"))
    if not url or url.startswith("//"):
        return None
    if url.startswith("#/"):
        url = url[1:]
    elif url.startswith("#"):
        return None
    parts = urlsplit(url)
    if parts.scheme or parts.netloc:
        return None
    path = unquote(parts.path)
    if not path or path == "/":
        return DOCS / "README.md"
    # Docsify renders its fallback document at the requested route; these links
    # deliberately target the site root rather than the fallback file's folder.
    base = DOCS if path.startswith("/") or source == DOCS / "src/inc/404.md" else source.parent
    target = base / path.lstrip("/")
    if not PurePosixPath(path).suffix:
        target = target / "README.md" if path.endswith("/") else target.with_suffix(".md")
    return target


def exact_file(path):
    """Validate each name on Windows too: GitHub Pages paths are case-sensitive."""
    try:
        # resolve() can replace the requested spelling with on-disk casing on
        # Windows. Keep the caller's spelling for the component-by-component check.
        relative = Path(os.path.abspath(path)).relative_to(DOCS)
        Path(path).resolve().relative_to(DOCS.resolve())
    except ValueError:
        return False
    current = DOCS
    for name in relative.parts:
        if not current.is_dir() or name not in {item.name for item in current.iterdir()}:
            return False
        current = current / name
    return current.is_file()


def npm_version(url):
    parts = urlsplit(url if not url.startswith("//") else "https:" + url)
    if parts.netloc == "cdn.jsdelivr.net" and parts.path.startswith("/npm/"):
        package_path = parts.path[len("/npm/"):]
    elif parts.netloc in ("unpkg.com", "www.unpkg.com"):
        package_path = parts.path.lstrip("/")
    else:
        return None
    match = re.match(r"(?:@[^/]+/[^/@]+|[^/@]+)@([^/]+)(?:/|$)", package_path)
    return bool(match and FULL_VERSION.fullmatch(match[1]))


def main():
    failures = []
    checked_links = 0
    for name in PAGES:
        source = DOCS / name
        if not exact_file(source):
            failures.append(f"docs/{name}: page missing or filename case differs")
            continue
        for url in markdown_urls(without_examples(read(source))):
            target = local_target(url, source)
            if target is not None:
                checked_links += 1
                if not exact_file(target):
                    failures.append(f"docs/{name}: local link missing or filename case differs")

    index = DOCS / "index.html"
    if not exact_file(index):
        failures.append("docs/index.html: missing")
    else:
        if not re.search(r'<html\s+[^>]*lang=[\"\']en[\"\']', read(index)):
            failures.append("docs/index.html: the default document language must be English")
        parser = References()
        parser.feed(re.sub(r"<!--.*?-->", "", read(index), flags=re.DOTALL))
        imports = re.findall(
            r"\bimport\s+(?:[^;'\"]*?\sfrom\s*)?['\"]([^'\"]+)['\"]",
            "\n".join(parser.script_text),
        )
        for url in parser.urls + imports:
            target = local_target(url, index)
            if target is not None:
                checked_links += 1
                if not exact_file(target):
                    failures.append("docs/index.html: local asset/link missing or filename case differs")
            if npm_version(url) is False:
                failures.append("docs/index.html: npm dependency lacks an exact full version")
        remote_scripts = []
        for url in parser.scripts + imports:
            parts = urlsplit(url if not url.startswith("//") else "https:" + url)
            if parts.netloc:
                remote_scripts.append((parts.netloc.lower(), parts.path))
        if any(count > 1 for count in Counter(remote_scripts).values()):
            failures.append("docs/index.html: duplicate remote script/import")

    for name in ("_navbar.md", "zh-cn/_navbar.md"):
        path = DOCS / name
        if path.is_file():
            for locale in ("en", "zh-cn"):
                if not re.search(r'data-site-language=[\"\']' + locale + r'[\"\']', read(path)):
                    failures.append(f"docs/{name}: missing language-switch option")

    public_text = {".md", ".html", ".js", ".json", ".txt", ".yaml", ".yml", ".css", ".svg"}
    for path in DOCS.rglob("*"):
        if path.is_file() and path.name.lower() == "san.html":
            failures.append("docs/: private login-page export san.html is publicly accessible")
        if path.is_file() and path.suffix.lower() in public_text and SENSITIVE.search(read(path)):
            # Never print matches or their values, including when a check fails.
            failures.append(f"{path.relative_to(ROOT).as_posix()}: sensitive session/join field found")

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        print(f"FAILED: {len(failures)} issue(s); no network requests made.")
        return 1
    print(f"PASS: {len(PAGES)} pages, {checked_links} local links/assets, pinned npm versions,")
    print("      unique remote scripts and public-content privacy checks; no network requests made.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
