from __future__ import annotations

import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
ASSET_EXTENSIONS = {
    ".css",
    ".eot",
    ".gif",
    ".jpeg",
    ".jpg",
    ".js",
    ".png",
    ".svg",
    ".ttf",
    ".webp",
    ".woff",
    ".woff2",
}
CSS_URL = re.compile(r"url\(([^)]*)\)", re.IGNORECASE)
UPLOAD_URL = re.compile(
    r"https?://(?:www\.)?nashvilletaxsolutions\.com/wp-content/uploads/[^\s\"'<>),]+"
)


class AssetReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "link" and attributes.get("rel") == "stylesheet":
            url = attributes.get("href")
        elif tag == "script":
            url = attributes.get("src")
        else:
            return

        if url and url.startswith(
            (
                "https://nashvilletaxsolutions.com/",
                "https://www.nashvilletaxsolutions.com/",
            )
        ):
            self.urls.add(url)


def local_asset_for_url(url: str, files: set[str]) -> str | None:
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    suffix = Path(filename).suffix
    version = next(
        (value for key, value in parse_qsl(parsed.query) if key == "ver"),
        None,
    )

    if version and suffix:
        versioned_name = f"{filename[:-len(suffix)]}_ver={version}{suffix}"
        if versioned_name in files:
            return versioned_name

    if filename in files:
        return filename

    if suffix:
        alternatives = sorted(
            name
            for name in files
            if name.startswith(f"{filename[:-len(suffix)]}_ver=")
            and Path(name).suffix == suffix
        )
        if len(alternatives) == 1:
            return alternatives[0]

    return None


def rewrite_css(css: str, files: set[str]) -> str:
    def rewrite_url(match: re.Match[str]) -> str:
        raw = match.group(1).strip()
        quote = raw[0] if raw[:1] in {"'", '"'} else ""
        value = raw[1:-1] if quote and raw.endswith(quote) else raw
        if value.startswith(("data:", "http:", "https:", "//", "#")):
            return match.group(0)

        basename = Path(unquote(urlparse(value).path)).name
        if not basename or basename not in files:
            return match.group(0)

        suffix = ""
        parsed = urlparse(value)
        if parsed.query:
            suffix += f"?{parsed.query}"
        if parsed.fragment:
            suffix += f"#{parsed.fragment}"
        return f'url("./{basename}{suffix}")'

    return CSS_URL.sub(rewrite_url, css)


def build(output: Path) -> None:
    output.mkdir(parents=True)

    shutil.copy2(ROOT / "index.html", output / "index.html")
    for directory in (
        "about-us",
        "community",
        "contact-us",
        "faq",
        "our-team",
        "services",
        "assets",
    ):
        shutil.copytree(ROOT / directory, output / directory, dirs_exist_ok=True)

    web_files = {
        path.name
        for path in WEB_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in ASSET_EXTENSIONS
    }
    local_web = output / "web"
    local_web.mkdir(exist_ok=True)
    for filename in web_files:
        source = WEB_DIR / filename
        destination = local_web / filename
        if source.suffix.lower() == ".css":
            destination.write_text(
                rewrite_css(source.read_text(errors="replace"), web_files),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source, destination)

    html_path = output / "index.html"
    html = html_path.read_text(encoding="utf-8")
    references = AssetReferences()
    references.feed(html)
    for url in references.urls:
        filename = local_asset_for_url(url, web_files)
        if filename:
            html = html.replace(url, f"web/{filename}")
        else:
            print(
                f"Warning: no local copy of {Path(urlparse(url).path).name}; "
                "omitting this stylesheet or script reference.",
                file=sys.stderr,
            )
            html = re.sub(
                rf"<(?:link|script)\b(?=[^>]*{re.escape(url)}).*?>",
                "",
                html,
                flags=re.IGNORECASE | re.DOTALL,
            )

    missing_uploads: set[str] = set()

    def rewrite_upload(match: re.Match[str]) -> str:
        filename = Path(unquote(urlparse(match.group(0)).path)).name
        if filename in web_files:
            return f"web/{filename}"
        missing_uploads.add(filename)
        return match.group(0)

    html = UPLOAD_URL.sub(rewrite_upload, html)
    if missing_uploads:
        print(
            f"Warning: {len(missing_uploads)} WordPress upload files have no local "
            "copy and remain external.",
            file=sys.stderr,
        )
    html_path.write_text(html, encoding="utf-8")
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_static_site.py OUTPUT_DIRECTORY")
    build(Path(sys.argv[1]).resolve())
