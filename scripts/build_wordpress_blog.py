from __future__ import annotations

import html
import json
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
UPLOADS = ROOT / "web" / "wp-content" / "uploads"
MANIFEST = ".wordpress-static-manifest.json"
WP_BLOG_URL = re.compile(
    r"https?://(?:www\.)?nashvilletaxsolutions\.com/blog/([A-Za-z0-9/_-]*)",
    re.IGNORECASE,
)
WP_SITE_URL = re.compile(
    r"https?://(?:www\.)?nashvilletaxsolutions\.com(?P<path>/[A-Za-z0-9/_-]*)"
    r"(?P<suffix>[?#][^\"']*)?",
    re.IGNORECASE,
)
WP_UPLOAD_URL = re.compile(
    r"https?://[^/\"'\s<>),]+/wp-content/uploads/[^\"'\s<>),]+"
    r"|(?<![A-Za-z0-9:/])/?wp-content/uploads/[^\"'\s<>),]+",
    re.IGNORECASE,
)
SQL_ESCAPES = {
    "0": "\0",
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "Z": "\x1a",
    "\\": "\\",
    "'": "'",
    '"': '"',
}


class TextContent(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def sql_value(raw: str) -> str | None:
    raw = raw.strip()
    if raw.upper() == "NULL":
        return None
    if not raw.startswith("'") or not raw.endswith("'"):
        return raw

    value: list[str] = []
    index = 1
    while index < len(raw) - 1:
        char = raw[index]
        if char == "\\" and index + 1 < len(raw) - 1:
            index += 1
            value.append(SQL_ESCAPES.get(raw[index], raw[index]))
        elif char == "'" and index + 1 < len(raw) - 1 and raw[index + 1] == "'":
            value.append("'")
            index += 1
        else:
            value.append(char)
        index += 1
    return "".join(value)


def sql_row(line: str, start: int) -> tuple[list[str | None], int]:
    fields: list[str | None] = []
    field_start = start + 1
    index = field_start
    depth = 1
    quoted = False

    while index < len(line):
        char = line[index]
        if quoted:
            if char == "\\":
                index += 2
                continue
            if char == "'":
                if index + 1 < len(line) and line[index + 1] == "'":
                    index += 2
                    continue
                quoted = False
        elif char == "'":
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                fields.append(sql_value(line[field_start:index]))
                return fields, index + 1
        elif char == "," and depth == 1:
            fields.append(sql_value(line[field_start:index]))
            field_start = index + 1
        index += 1

    raise ValueError("Unterminated row in WordPress SQL dump")


def statement_rows(line: str, first_line: bool) -> list[list[str | None]]:
    start = line.find("VALUES") + len("VALUES") if first_line else 0
    rows: list[list[str | None]] = []
    while start < len(line):
        start = line.find("(", start)
        if start < 0:
            break
        row, start = sql_row(line, start)
        rows.append(row)
    return rows


def load_wordpress_data(sql_dump: Path) -> tuple[list[dict[str, str]], dict[int, str]]:
    posts: list[dict[str, str]] = []
    attachments: dict[int, str] = {}
    thumbnails: dict[int, int] = {}
    active_columns: list[str] = []
    active_table = ""
    insert_pattern = re.compile(r"INSERT INTO `([^`]+)`")

    with sql_dump.open("r", encoding="utf-8", errors="replace") as source:
        for line_number, line in enumerate(source, 1):
            match = insert_pattern.match(line)
            first_line = match is not None
            if match:
                table = match.group(1)
                if table.endswith("_posts") or table.endswith("_postmeta"):
                    active_table = table.rsplit("_", 1)[-1]
                    header = line[: line.find("VALUES")]
                    column_list = re.search(r"\(([^()]*)\)", header)
                    active_columns = (
                        re.findall(r"`([^`]+)`", column_list.group(1))
                        if column_list
                        else []
                    )
                else:
                    active_table = ""
                    active_columns = []

            if active_table and active_columns and (not first_line or "VALUES" in line):
                rows = statement_rows(line, first_line)
                for values in rows:
                    if len(values) != len(active_columns):
                        raise ValueError(
                            f"Unexpected column count in WordPress {active_table} row "
                            f"at line {line_number}: expected {len(active_columns)}, "
                            f"found {len(values)} in columns "
                            f"{', '.join(active_columns)}"
                        )
                    row = dict(zip(active_columns, values))
                    if active_table == "posts":
                        post_id = int(row["ID"] or 0)
                        post_type = row["post_type"]
                        if post_type == "attachment":
                            attachments[post_id] = row["guid"] or ""
                        elif (
                            post_type == "post"
                            and row["post_status"] == "publish"
                        ):
                            posts.append(
                                {
                                    "id": str(post_id),
                                    "title": row["post_title"] or "",
                                    "slug": row["post_name"] or "",
                                    "date": row["post_date"] or "",
                                    "content": row["post_content"] or "",
                                    "excerpt": row["post_excerpt"] or "",
                                }
                            )
                    elif (
                        row["meta_key"] == "_thumbnail_id"
                        and row["meta_value"]
                        and str(row["meta_value"]).isdigit()
                    ):
                        thumbnails[int(row["post_id"] or 0)] = int(row["meta_value"])

            if active_table and line.rstrip().endswith(";"):
                active_table = ""
                active_columns = []

    for post in posts:
        attachment_id = thumbnails.get(int(post["id"]))
        if attachment_id:
            post["image"] = attachments.get(attachment_id, "")
    return posts, attachments


def clean_slug(value: str, post_id: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", value.casefold()).strip("-")
    return slug or f"post-{post_id}"


def text_excerpt(content: str) -> str:
    parser = TextContent()
    parser.feed(content)
    text = " ".join(" ".join(parser.parts).split())
    return text[:237].rstrip() + ("..." if len(text) > 240 else "")


def relative_upload_path(url: str) -> tuple[Path, str] | None:
    parsed = urlparse(url)
    path = unquote(parsed.path)
    marker = "/wp-content/uploads/"
    marker_index = path.find(marker)
    if marker_index < 0:
        marker = "wp-content/uploads/"
        marker_index = path.find(marker)
    if marker_index < 0:
        return None

    relative = Path(path[marker_index + len(marker) :])
    if not relative.parts or ".." in relative.parts:
        return None
    source = (UPLOADS / relative).resolve()
    try:
        source.relative_to(UPLOADS.resolve())
    except ValueError:
        return None
    suffix = f"?{parsed.query}" if parsed.query else ""
    suffix += f"#{parsed.fragment}" if parsed.fragment else ""
    return source, relative.as_posix() + suffix


def rewrite_uploads(
    content: str,
    page_depth: int,
    output: Path,
    generated: set[str],
) -> str:
    prefix = "../" * page_depth + "media/"

    def replace(match: re.Match[str]) -> str:
        found = relative_upload_path(match.group(0))
        if not found:
            return match.group(0)
        source, relative = found
        media_path, separator, suffix = relative.partition("?")
        if not source.is_file():
            return match.group(0)
        destination = output / "media" / media_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copy2(source, destination)
        generated.add(destination.relative_to(output).as_posix())
        return prefix + media_path + (separator + suffix if separator else "")

    return WP_UPLOAD_URL.sub(replace, content)


def rewrite_blog_links(content: str, slugs: set[str]) -> str:
    content = WP_BLOG_URL.sub(
        lambda match: "../" + match.group(1).strip("/") + "/",
        content,
    )

    def local_target(path: str) -> str | None:
        parts = [part for part in path.split("/") if part]
        if not parts:
            return "../../"
        if parts[0] in {"about-us", "community", "contact-us", "faq", "our-team", "services"}:
            return f'../../{parts[0]}/'
        if parts[0] == "service":
            return "../../services/"
        if parts[0] == "blog":
            if len(parts) > 1 and parts[1] in slugs:
                return f'../{parts[1]}/'
            return "../"
        if parts[0] in slugs:
            return f'../{parts[0]}/'
        return None

    def replace_site_url(match: re.Match[str]) -> str:
        target = local_target(match.group("path"))
        if target is None:
            return match.group(0)
        return target + (match.group("suffix") or "")

    content = WP_SITE_URL.sub(replace_site_url, content)
    relative_path = re.compile(
        r"(?P<quote>[\"'])(?P<path>(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+/?)"
        r"(?P<suffix>[?#][^\"']*)?(?P=quote)"
    )

    def replace_relative_path(match: re.Match[str]) -> str:
        target = local_target(match.group("path"))
        if target is None:
            return match.group(0)
        suffix = match.group("suffix") or ""
        return f'{match.group("quote")}{target}{suffix}{match.group("quote")}'

    content = relative_path.sub(replace_relative_path, content)
    root_path = re.compile(
        r"(?P<quote>[\"'])(?P<path>/[A-Za-z0-9/_-]*)"
        r"(?P<suffix>[?#][^\"']*)?(?P=quote)"
    )

    def replace_root_path(match: re.Match[str]) -> str:
        target = local_target(match.group("path"))
        if target is None:
            return match.group(0)
        suffix = match.group("suffix") or ""
        return f'{match.group("quote")}{target}{suffix}{match.group("quote")}'

    return root_path.sub(replace_root_path, content)


def read_manifest(output: Path) -> list[str]:
    manifest_path = output / MANIFEST
    if not manifest_path.is_file():
        return []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise ValueError(f"Invalid generated file manifest: {manifest_path}")
    return data


def clean_previous_output(output: Path) -> None:
    for relative in read_manifest(output):
        target = (output / relative).resolve()
        try:
            target.relative_to(output.resolve())
        except ValueError as error:
            raise ValueError(f"Unsafe path in generated file manifest: {relative}") from error
        if target.is_file():
            target.unlink()


def page_shell(title: str, description: str, depth: int, body: str) -> str:
    root = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;600;700&amp;family=Source+Sans+Pro:wght@400;600;700&amp;display=swap">
  <link rel="stylesheet" href="{root}assets/css/contact-pages.css">
  <link rel="stylesheet" href="{root}assets/css/blog.css">
</head>
<body class="nts-reference-page">
  <header class="blog-header">
    <div class="blog-nav">
      <a class="blog-brand" href="{root}" aria-label="Nashville Tax Solutions home">
        <img src="{root}assets/images/reference-team/main-company-logo.webp" alt="Nashville Tax Solutions">
      </a>
      <nav aria-label="Main navigation">
        <a href="{root}">Home</a><a href="{root}about-us/">About Us</a>
        <a href="{root}services/">Services</a><a href="{root}our-team/">Our Team</a>
        <a href="{root}blog/" aria-current="page">Blog</a>
      </nav>
      <a class="blog-contact" href="{root}contact-us/">Contact Us</a>
    </div>
  </header>
  <main class="blog-main">{body}</main>
  <footer class="nts-footer">
    <div class="nts-content nts-footer-grid">
      <div><h2>Nashville Tax Solutions</h2><p>Personalized tax preparation, representation, and resolution support for individuals and businesses.</p></div>
      <div><h2>Offices</h2>
        <address><strong>West Palm Beach Office</strong><br><a class="nts-map-link" href="https://maps.app.goo.gl/TqJXwEf6KLxiqKqd7" target="_blank" rel="noopener noreferrer"><svg class="nts-map-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 22s8-7.16 8-13a8 8 0 1 0-16 0c0 5.84 8 13 8 13Z" fill="#EA4335"/><circle cx="12" cy="9" r="2.8" fill="#fff"/></svg><span>Google Maps</span></a><br>500 S. Australian Ave Suite 705, West Palm Beach, FL 33401</address>
        <address><strong>Fort Pierce Office</strong><br><a class="nts-map-link" href="https://maps.app.goo.gl/4Vv7syZXac9RkJjM7" target="_blank" rel="noopener noreferrer"><svg class="nts-map-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 22s8-7.16 8-13a8 8 0 1 0-16 0c0 5.84 8 13 8 13Z" fill="#EA4335"/><circle cx="12" cy="9" r="2.8" fill="#fff"/></svg><span>Google Maps</span></a><br>130 S. Indian River Dr Ste 405, Fort Pierce, FL 34950</address>
        <address><strong>Nashville Office</strong><br><a class="nts-map-link" href="https://www.google.com/maps/search/?api=1&amp;query=1801+West+End+Avenue%2C+Suite+1000%2C+Nashville%2C+TN+37203" target="_blank" rel="noopener noreferrer"><svg class="nts-map-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 22s8-7.16 8-13a8 8 0 1 0-16 0c0 5.84 8 13 8 13Z" fill="#EA4335"/><circle cx="12" cy="9" r="2.8" fill="#fff"/></svg><span>Google Maps</span></a><br>1801 West End Avenue, Suite 1000, Nashville, TN 37203</address>
      </div>
      <div><h2>Quick Links</h2><nav aria-label="Footer navigation"><a href="{root}">Home</a><a href="{root}our-team/">Our Team</a><a href="{root}community/">Community</a><a href="{root}faq/">FAQ</a><a href="{root}contact-us/">Contact</a><a href="mailto:info@nashvilletaxsolutions.com">info@nashvilletaxsolutions.com</a></nav></div>
    </div>
    <div class="nts-footer-bottom">© <span class="nts-year">2026</span> Nashville Tax Solutions. All rights reserved.</div>
  </footer>
  <script>document.querySelectorAll(".nts-year").forEach(function (year) {{ year.textContent = new Date().getFullYear(); }});</script>
</body>
</html>
"""


def generate(posts: list[dict[str, str]], output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    clean_previous_output(output)
    generated: set[str] = set()
    used_slugs: set[str] = set()
    posts.sort(key=lambda post: (post["date"], post["id"]), reverse=True)

    for post in posts:
        slug = clean_slug(post["slug"], post["id"])
        if slug in used_slugs:
            slug = f"{slug}-{post['id']}"
        used_slugs.add(slug)
        post["output_slug"] = slug

    entries: list[str] = []
    for post in posts:
        slug = post["output_slug"]
        post_dir = output / slug
        post_dir.mkdir(parents=True, exist_ok=True)
        content = rewrite_blog_links(
            rewrite_uploads(post["content"], 1, output, generated),
            used_slugs,
        )
        excerpt = post["excerpt"] or text_excerpt(post["content"])
        image_html = ""
        if post.get("image"):
            image_url = rewrite_uploads(post["image"], 1, output, generated)
            if image_url != post["image"]:
                image_html = (
                    f'<img class="post-image" src="{html.escape(image_url, quote=True)}" '
                    f'alt="{html.escape(post["title"], quote=True)}">'
                )

        article = (
            f'<article class="post"><p class="post-date">'
            f'{html.escape(post["date"][:10])}</p>'
            f'<h1>{html.escape(post["title"])}</h1>{image_html}'
            f'<div class="post-content">{content}</div>'
            f'<p><a class="back-link" href="../">Back to all articles</a></p></article>'
        )
        page = page_shell(
            f'{post["title"]} | Nashville Tax Solutions',
            excerpt,
            2,
            article,
        )
        page_path = post_dir / "index.html"
        page_path.write_text(page, encoding="utf-8")
        generated.add(page_path.relative_to(output).as_posix())

        index_image = ""
        if post.get("image"):
            image_url = rewrite_uploads(post["image"], 0, output, generated)
            if image_url != post["image"]:
                index_image = (
                    f'<img src="{html.escape(image_url, quote=True)}" '
                    f'alt="" loading="lazy">'
                )
        entries.append(
            f'<article class="post-card">{index_image}<div>'
            f'<p class="post-date">{html.escape(post["date"][:10])}</p>'
            f'<h2><a href="{html.escape(slug, quote=True)}/">'
            f'{html.escape(post["title"])}</a></h2>'
            f'<p>{html.escape(excerpt)}</p>'
            f'<a class="read-more" href="{html.escape(slug, quote=True)}/">'
            "Read article</a></div></article>"
        )

    body = (
        '<section class="blog-hero"><div class="blog-hero-content">'
        '<p class="blog-eyebrow">Nashville Tax Solutions</p>'
        '<h1 class="page-title">Tax Tips &amp; News</h1>'
        '<p class="page-intro">Clear guidance and practical insights for your tax questions.</p>'
        '</div></section>'
        + "".join(entries)
    )
    index = page_shell(
        "Blog | Nashville Tax Solutions",
        "Tax advice, news, and updates from Nashville Tax Solutions.",
        1,
        body,
    )
    index_path = output / "index.html"
    index_path.write_text(index, encoding="utf-8")
    generated.add("index.html")

    (output / MANIFEST).write_text(
        json.dumps(sorted(generated), indent=2) + "\n",
        encoding="utf-8",
    )
    return len(posts)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: build_wordpress_blog.py SQL_DUMP UPLOADS_DIRECTORY OUTPUT_DIRECTORY"
        )
    global UPLOADS
    sql_dump, uploads, output = map(Path, sys.argv[1:])
    UPLOADS = uploads.resolve()
    posts, _ = load_wordpress_data(sql_dump)
    count = generate(posts, output.resolve())
    print(f"Generated {count} published blog posts in {output}")


if __name__ == "__main__":
    main()
