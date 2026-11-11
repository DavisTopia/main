from __future__ import annotations

import re
import shutil
import sys
from html.parser import HTMLParser
from os.path import relpath
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse, urlunparse
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
ASSET_SOURCE = ROOT / "assets" / "vendor" / "wordpress"
ASSET_EXTENSIONS = {
    ".css",
    ".eot",
    ".gif",
    ".jpeg",
    ".jpg",
    ".js",
    ".mp4",
    ".png",
    ".svg",
    ".ttf",
    ".webp",
    ".woff",
    ".woff2",
}
CSS_URL = re.compile(r"url\(([^)]*)\)", re.IGNORECASE)
WP_ASSET_URL = re.compile(
    r"https?://(?:www\.)?nashvilletaxsolutions\.com/(?:wp-content|wp-includes)/[^\s\"'<>),\\]+"
)
WP_HOSTS = {"nashvilletaxsolutions.com", "www.nashvilletaxsolutions.com"}
UPLOAD_FALLBACKS = {
    "business-people-laptop-planning-while-reading-email-information-online-with-lawyer-client-men-together-meeting-discussion-with-company-wifi-internet-research-case-advice.png": "businessmen-having-discussion-digital-tablet.png",
}
CSS_FALLBACKS = {"widget_banner.jpg": "CTA-section-background.webp"}
SITE_URL = "https://nashvilletaxsolutions.com"
LEGACY_LINK_REWRITES = {
    "https://nashvilletaxsolutions.com/service-areas/fort-pierce/":
        "https://nashvilletaxsolutions.com/contact-us/",
    "https://nashvilletaxsolutions.com/service-areas/west-palm-beach/":
        "https://nashvilletaxsolutions.com/contact-us/",
    "https://nashvilletaxsolutions.com/service-areas/fort-pierce/enrolled-agent/":
        "https://nashvilletaxsolutions.com/contact-us/",
    "https://nashvilletaxsolutions.com/service-areas/west-palm-beach/enrolled-agent/":
        "https://nashvilletaxsolutions.com/contact-us/",
    "https://nashvilletaxsolutions.com/tax-resolution-services/":
        "https://nashvilletaxsolutions.com/services/#tax-resolution",
    "https://nashvilletaxsolutions.com/business-advisory-services/":
        "https://nashvilletaxsolutions.com/services/#business-advisory",
    "https://nashvilletaxsolutions.com/contact-us/enrolled-agent/":
        "https://nashvilletaxsolutions.com/contact-us/",
}


class IndexingMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonical = ""
        self.og_url = ""
        self.noindex = False
        self.redirect = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "link" and "canonical" in (attributes.get("rel") or "").lower():
            self.canonical = attributes.get("href") or ""
        elif tag == "meta" and (attributes.get("property") or "").lower() == "og:url":
            self.og_url = attributes.get("content") or ""
        elif tag == "meta":
            name = (attributes.get("name") or "").lower()
            content = (attributes.get("content") or "").lower()
            if name == "robots" and "noindex" in content:
                self.noindex = True
            if (attributes.get("http-equiv") or "").lower() == "refresh":
                self.redirect = True


def ensure_canonical_metadata(html: str, html_path: Path, output: Path) -> str:
    metadata = IndexingMetadata()
    metadata.feed(html)
    if metadata.noindex or metadata.redirect or metadata.canonical:
        return html

    relative = html_path.parent.relative_to(output)
    route = "/" if str(relative) == "." else f"/{relative.as_posix()}/"
    canonical = f"{SITE_URL}{route}"
    tags = (
        f'<link rel="canonical" href="{canonical}">\n'
        f'<meta property="og:url" content="{canonical}">\n'
    )
    return re.sub(r"</head\s*>", f"{tags}</head>", html, count=1, flags=re.IGNORECASE)


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


def browser_assets() -> set[Path]:
    return {
        path
        for path in ASSET_SOURCE.rglob("*")
        if path.is_file() and path.suffix.lower() in ASSET_EXTENSIONS
    }


def local_asset_for_url(url: str, files: set[Path]) -> Path | None:
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    suffix = Path(filename).suffix
    version = next(
        (value for key, value in parse_qsl(parsed.query) if key == "ver"),
        None,
    )

    path_parts = [unquote(part) for part in parsed.path.split("/") if part]
    for root_name in ("wp-content", "wp-includes"):
        for root_index, part in enumerate(path_parts):
            if part == root_name:
                candidate = ASSET_SOURCE.joinpath(*path_parts[root_index:])
                if candidate in files:
                    return candidate

    if version and suffix:
        versioned_name = f"{filename[:-len(suffix)]}_ver={version}{suffix}"
        candidate = ASSET_SOURCE / versioned_name
        if candidate in files:
            return candidate

    direct = ASSET_SOURCE / filename
    if direct in files:
        return direct

    if suffix:
        alternatives = sorted(
            path
            for path in files
            if path.name.startswith(f"{filename[:-len(suffix)]}_ver=")
            and path.suffix == suffix
        )
        if len(alternatives) == 1:
            return alternatives[0]

    alternatives = sorted(path for path in files if path.name == filename)
    if len(alternatives) == 1:
        return alternatives[0]

    fallback_name = UPLOAD_FALLBACKS.get(filename)
    if fallback_name:
        fallback = ASSET_SOURCE / fallback_name
        if fallback in files:
            return fallback

    return None


def rewrite_css(
    css: str,
    source: Path,
    output_path: Path,
    output_root: Path,
    files: set[Path],
    dependencies: set[Path],
    missing_dependencies: set[str],
) -> str:
    def rewrite_url(match: re.Match[str]) -> str:
        raw = match.group(1).strip()
        quote = raw[0] if raw[:1] in {"'", '"'} else ""
        value = raw[1:-1] if quote and raw.endswith(quote) else raw
        if value.startswith(("data:", "//", "#")):
            return match.group(0)

        parsed = urlparse(value)
        if parsed.scheme in {"http", "https"}:
            if parsed.hostname not in WP_HOSTS:
                return match.group(0)
            asset = local_asset_for_url(value, files)
        else:
            relative = (source.parent / unquote(parsed.path)).resolve()
            try:
                relative.relative_to(ASSET_SOURCE.resolve())
                asset = relative if relative in files else None
            except ValueError:
                asset = None
            if asset is None:
                basename = Path(unquote(parsed.path)).name
                matches = [path for path in files if path.name == basename]
                asset = matches[0] if len(matches) == 1 else None
            if asset is None:
                fallback_name = CSS_FALLBACKS.get(Path(unquote(parsed.path)).name)
                fallback = ASSET_SOURCE / fallback_name if fallback_name else None
                asset = fallback if fallback in files else None

        if asset is None:
            missing_dependencies.add(
                f"{source.relative_to(ASSET_SOURCE)}: {value}"
            )
            return match.group(0)

        dependencies.add(asset)
        asset_output = output_root / "web" / asset.relative_to(ASSET_SOURCE)
        local_path = relpath(asset_output, output_path.parent).replace("\\", "/")
        rewritten = urlunparse(("", "", local_path, "", parsed.query, parsed.fragment))
        return f"url({quote}{rewritten}{quote})"

    return CSS_URL.sub(rewrite_url, css)


def rewrite_html_assets(
    html: str,
    html_path: Path,
    output_root: Path,
    files: set[Path],
    dependencies: set[Path],
    missing_resources: set[str],
    missing_assets: set[str],
) -> str:
    references = AssetReferences()
    references.feed(html)
    for url in sorted(references.urls):
        asset = local_asset_for_url(url, files)
        if asset:
            dependencies.add(asset)
            asset_output = output_root / "web" / asset.relative_to(ASSET_SOURCE)
            local_path = relpath(asset_output, html_path.parent).replace("\\", "/")
            html = html.replace(url, local_path)
        else:
            missing_resources.add(Path(urlparse(url).path).name)
            html = re.sub(
                rf"<(?:link|script)\b(?=[^>]*{re.escape(url)}).*?>",
                "",
                html,
                flags=re.IGNORECASE | re.DOTALL,
            )

    def rewrite_wp_asset(match: re.Match[str]) -> str:
        asset = local_asset_for_url(match.group(0), files)
        if asset:
            dependencies.add(asset)
            asset_output = output_root / "web" / asset.relative_to(ASSET_SOURCE)
            local_path = relpath(asset_output, html_path.parent).replace("\\", "/")
            return local_path
        filename = Path(unquote(urlparse(match.group(0)).path)).name
        missing_assets.add(filename)
        return match.group(0)

    return WP_ASSET_URL.sub(rewrite_wp_asset, html)


def generate_seo_files(output: Path) -> None:
    sitemap_urls: set[str] = set()
    for html_path in sorted(output.rglob("index.html")):
        html = html_path.read_text(encoding="utf-8")
        metadata = IndexingMetadata()
        metadata.feed(html)
        if metadata.noindex or metadata.redirect:
            continue

        if metadata.canonical:
            canonical = metadata.canonical
            parsed = urlparse(canonical)
            if parsed.hostname not in {
                "nashvilletaxsolutions.com",
                "www.nashvilletaxsolutions.com",
            }:
                continue
        else:
            relative = html_path.parent.relative_to(output)
            route = "/" if str(relative) == "." else f"/{relative.as_posix()}/"
            canonical = f"{SITE_URL}{route}"
        sitemap_urls.add(canonical)

    url_entries = "".join(
        f"<url><loc>{escape(url)}</loc></url>"
        for url in sorted(sitemap_urls)
    )
    (output / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{url_entries}</urlset>\n",
        encoding="utf-8",
    )
    (output / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )


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
        "service-areas",
        "privacy-policy",
        "terms-and-condition",
        "opt-in-for-tax-alerts",
        "tax-resolution-services",
        "business-advisory-services",
    ):
        shutil.copytree(ROOT / directory, output / directory, dirs_exist_ok=True)
    shutil.copytree(
        ROOT / "blog",
        output / "blog",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".wordpress-static-manifest.json"),
    )
    shutil.copytree(
        ROOT / "assets",
        output / "assets",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("vendor"),
    )

    web_files = browser_assets()
    pending: set[Path] = set()
    missing_resources: set[str] = set()
    missing_assets: set[str] = set()
    for html_path in output.rglob("*.html"):
        html = html_path.read_text(encoding="utf-8")
        blog_link = relpath(output / "blog", html_path.parent).replace("\\", "/")
        if not blog_link.endswith("/"):
            blog_link += "/"
        html = html.replace(
            "https://nashvilletaxsolutions.com/blog/",
            blog_link,
        ).replace(
            "https://www.nashvilletaxsolutions.com/blog/",
            blog_link,
        )
        for old_url, new_url in LEGACY_LINK_REWRITES.items():
            html = html.replace(old_url, new_url)
        html = rewrite_html_assets(
            html,
            html_path,
            output,
            web_files,
            pending,
            missing_resources,
            missing_assets,
        )
        if html_path.name == "index.html":
            html = ensure_canonical_metadata(html, html_path, output)
        html_path.write_text(html, encoding="utf-8")

    for resource in sorted(missing_resources):
        print(
            f"Warning: no local copy of {resource}; "
            "omitting its stylesheet or script reference.",
            file=sys.stderr,
        )
    for asset in sorted(missing_assets):
        print(
            f"Warning: no local copy of WordPress asset {asset}; "
            "it remains external.",
            file=sys.stderr,
        )

    missing_css_dependencies: set[str] = set()
    while pending:
        asset = pending.pop()
        destination = output / "web" / asset.relative_to(ASSET_SOURCE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if asset.suffix.lower() == ".css":
            css = asset.read_text(encoding="utf-8", errors="replace")
            destination.write_text(
                rewrite_css(
                    css,
                    asset,
                    destination,
                    output,
                    web_files,
                    pending,
                    missing_css_dependencies,
                ),
                encoding="utf-8",
            )
        else:
            shutil.copy2(asset, destination)

    for dependency in sorted(missing_css_dependencies):
        print(
            f"Warning: no local copy of CSS dependency {dependency}.",
            file=sys.stderr,
        )

    generate_seo_files(output)
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_static_site.py OUTPUT_DIRECTORY")
    build(Path(sys.argv[1]).resolve())
