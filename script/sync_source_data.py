#!/usr/bin/env python3
"""Sync site CSV data from https://addekth.github.io/publications/."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag

SOURCE_URL = "https://addekth.github.io/publications/"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "item"


def sanitize_label(label: str) -> str:
    label = normalize_text(label).replace("|", "/").replace(";", ",")
    return label or "link"


def normalize_url(url: str) -> str:
    url = normalize_text(url)
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        return url

    parts = urlsplit(url)
    path = quote(parts.path, safe="/%:@-._~!$&'()*+,;=")
    query = quote(parts.query, safe="=%&:@-._~!$'()*+,;/?")
    fragment = quote(parts.fragment, safe="=%&:@-._~!$'()*+,;/?")
    return urlunsplit((parts.scheme, parts.netloc, path, query, fragment))


def unique_anchors(node: Tag) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for anchor in node.find_all("a"):
        url = normalize_url(anchor.get("href", ""))
        if not url:
            continue
        label = sanitize_label(anchor.get_text(" ", strip=True))
        items.append((label, url))

    dedup = []
    seen = set()
    for label, url in items:
        key = (label.lower(), url)
        if key in seen:
            continue
        seen.add(key)
        dedup.append((label, url))

    label_counter: Counter[str] = Counter()
    normalized: list[tuple[str, str]] = []
    for label, url in dedup:
        label_counter[label.lower()] += 1
        count = label_counter[label.lower()]
        final_label = label if count == 1 else f"{label}_{count}"
        normalized.append((final_label, url))
    return normalized


def links_to_csv(links: Iterable[tuple[str, str]]) -> str:
    return ";".join(f"{label}|{url}" for label, url in links)


def text_without_anchor_labels(node: Tag) -> str:
    # Work on a detached copy so we can strip anchor labels without mutating source soup.
    temp = BeautifulSoup(str(node), "html.parser")
    for anchor in temp.find_all("a"):
        anchor.replace_with(" ")
    return normalize_text(temp.get_text(" ", strip=True))


def find_level1(soup: BeautifulSoup, summary_text: str) -> Tag:
    for detail in soup.select("details.level-1"):
        summary = detail.find("summary")
        if summary and normalize_text(summary.get_text()) == summary_text:
            return detail
    raise ValueError(f"Unable to find level-1 section: {summary_text}")


def find_level2(section: Tag, summary_text: str) -> Tag:
    for detail in section.select("details.level-2"):
        summary = detail.find("summary")
        if summary and normalize_text(summary.get_text()) == summary_text:
            return detail
    raise ValueError(f"Unable to find level-2 section: {summary_text}")


def list_items(level2: Tag) -> list[Tag]:
    return list(level2.select("ul.cv-list > li"))


def row_container(li: Tag) -> Tag:
    div = li.find("div")
    if div is not None:
        return div
    spans = li.find_all("span")
    if len(spans) > 1:
        return spans[-1]
    return li


def first_text_before(node: Tag, stop_tag: str, stop_class: str | None = None) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, Tag):
            classes = child.get("class", [])
            if child.name == stop_tag and (stop_class is None or stop_class in classes):
                break
            parts.append(child.get_text(" ", strip=True))
        else:
            parts.append(str(child))
    return normalize_text(" ".join(parts))


def parse_cv_general(soup: BeautifulSoup, about_section: Tag) -> list[dict[str, str]]:
    header = soup.find("header")
    kth_url = "https://www.kth.se/profile/adde"
    if header is not None:
        for anchor in header.find_all("a"):
            if normalize_text(anchor.get_text()).lower() == "kth":
                kth_url = normalize_text(anchor.get("href", kth_url))
                break

    employments = find_level2(about_section, "Employments")
    affiliation = "KTH Royal Institute of Technology"
    department = "Division of Structural Engineering and Bridges"
    for li in list_items(employments):
        text = text_without_anchor_labels(row_container(li))
        m = re.search(r"Royal Institute of Technology \(KTH\),\s*([^.,]+)", text)
        if m:
            department = normalize_text(m.group(1))
            department = re.sub(r"\blink\b$", "", department, flags=re.IGNORECASE).strip(" ,.;")
            break

    return [
        {
            "affiliation": affiliation,
            "department": department,
            "profile_url": kth_url,
        }
    ]


def parse_external_profiles(soup: BeautifulSoup) -> list[dict[str, str]]:
    wanted = {"ORCiD", "KTH", "DiVA", "ResearchGate", "Google Scholar"}
    header = soup.find("header")
    if header is None:
        return []

    rows = []
    for anchor in header.find_all("a"):
        label = normalize_text(anchor.get_text())
        if label not in wanted:
            continue
        rows.append({"label": label, "url": normalize_text(anchor.get("href", ""))})

    # keep stable order
    order = ["ORCiD", "KTH", "DiVA", "ResearchGate", "Google Scholar"]
    rows.sort(key=lambda r: order.index(r["label"]) if r["label"] in order else 99)
    return rows


def parse_cv_employments(about_section: Tag) -> list[dict[str, str]]:
    section = find_level2(about_section, "Employments")
    rows = []
    for li in list_items(section):
        period = normalize_text(li.select_one(".cv-year").get_text(" ", strip=True))
        body = row_container(li)
        full = normalize_text(body.get_text(" ", strip=True))
        title = normalize_text(full.split(",", 1)[0])
        italics = [normalize_text(i.get_text(" ", strip=True)) for i in body.find_all("i")]
        italics = [x for x in italics if x]
        org = " | ".join(dict.fromkeys(italics))
        if not org and "," in full:
            org = normalize_text(full.split(",", 1)[1])
        rows.append(
            {
                "period": period,
                "title": title,
                "org": org,
                "links": links_to_csv(unique_anchors(body)),
            }
        )
    return rows


def parse_cv_international(about_section: Tag) -> list[dict[str, str]]:
    section = find_level2(about_section, "International")
    rows = []
    for li in list_items(section):
        period = normalize_text(li.select_one(".cv-year").get_text(" ", strip=True))
        body = row_container(li)
        full = text_without_anchor_labels(body)
        title = normalize_text(full.split(",", 1)[0])
        italics = [normalize_text(i.get_text(" ", strip=True)).strip(" ,") for i in body.find_all("i")]
        italics = [x for x in italics if x]
        org = ", ".join(dict.fromkeys(italics))

        location = ""
        if org and "," in org and "|" not in org:
            location = normalize_text(org.rsplit(",", 1)[1]).strip(" .")

        rows.append(
            {
                "period": period,
                "title": title,
                "org": org,
                "location": location,
                "links": links_to_csv(unique_anchors(body)),
                "notes": full,
            }
        )
    return rows


def parse_cv_awards(about_section: Tag) -> list[dict[str, str]]:
    section = find_level2(about_section, "Awards & Scholarships")
    rows = []
    for li in list_items(section):
        year = normalize_text(li.select_one(".cv-year").get_text(" ", strip=True))
        body = row_container(li)
        rows.append(
            {
                "year": year,
                "item": text_without_anchor_labels(body),
                "links": links_to_csv(unique_anchors(body)),
            }
        )
    return rows


def parse_projects_commission(about_section: Tag) -> list[dict[str, str]]:
    section = find_level2(about_section, "Commission of Trust")
    rows = []
    for li in list_items(section):
        period = normalize_text(li.select_one(".cv-year").get_text(" ", strip=True))
        body = row_container(li)
        rows.append(
            {
                "period": period,
                "title": normalize_text(body.get_text(" ", strip=True)),
                "links": links_to_csv(unique_anchors(body)),
            }
        )
    return rows


def text_before_first_br(node: Tag) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, Tag) and child.name == "br":
            break
        if isinstance(child, Tag):
            parts.append(child.get_text(" ", strip=True))
        else:
            parts.append(str(child))
    return normalize_text(" ".join(parts))


def parse_projects_research(about_section: Tag) -> list[dict[str, str]]:
    section = find_level2(about_section, "Research Projects")
    rows = []
    for li in list_items(section):
        year = normalize_text(li.select_one(".cv-year").get_text(" ", strip=True))
        body = row_container(li)
        full = normalize_text(body.get_text(" ", strip=True))
        title = text_before_first_br(body)
        if not title:
            title = normalize_text(full.split(".", 1)[0])

        description = full
        if description.startswith(title):
            description = normalize_text(description[len(title) :].lstrip(" .,-"))

        rows.append(
            {
                "year": year,
                "title": title,
                "description": description,
                "links": links_to_csv(unique_anchors(body)),
            }
        )
    return rows


def parse_teaching_phd(teaching_section: Tag) -> list[dict[str, str]]:
    section = find_level2(teaching_section, "PhD Students")
    rows = []
    for li in list_items(section):
        period = normalize_text(li.select_one(".cv-year").get_text(" ", strip=True))
        body = row_container(li)
        full = normalize_text(body.get_text(" ", strip=True))

        name = ""
        for pattern in (
            r"Ph\.?D(?:\.|-) ?Student\s+([^,.;()]+)",
            r"PhD-student\s+([^,.;()]+)",
            r"Ph\.D\. Student\s+([^,.;()]+)",
        ):
            m = re.search(pattern, full, flags=re.IGNORECASE)
            if m:
                name = normalize_text(m.group(1))
                break
        if not name:
            name = normalize_text(full.split(".", 1)[0])

        status = first_text_before(body, "span", "course-details")
        if not status:
            status = normalize_text(full.split(".", 1)[0])
        status = status.rstrip(" ,.;")

        rows.append(
            {
                "name": name,
                "status": status,
                "period": period,
                "links": links_to_csv(unique_anchors(body)),
            }
        )
    return rows


def parse_teaching_master(teaching_section: Tag) -> list[dict[str, str]]:
    section = find_level2(teaching_section, "Master Students")
    rows = []
    for li in list_items(section):
        body = row_container(li)
        full = text_without_anchor_labels(body)
        m = re.match(r"^(?P<names>.+),\s*(?P<year>(?:19|20)\d{2})\.\s*(?P<title>.+)$", full)
        if m:
            names = normalize_text(m.group("names"))
            year = normalize_text(m.group("year"))
            title = normalize_text(m.group("title"))
        else:
            names = full
            year = ""
            title = full

        rows.append(
            {
                "name": names,
                "status": title,
                "period": year,
                "links": links_to_csv(unique_anchors(body)),
            }
        )
    return rows


def parse_teaching_courses(teaching_section: Tag) -> list[dict[str, str]]:
    section = find_level2(teaching_section, "Courses")
    rows = []
    for li in list_items(section):
        code_node = li.select_one(".cv-year")
        code = normalize_text(code_node.get_text(" ", strip=True)) if code_node else ""
        body = row_container(li)
        full = normalize_text(body.get_text(" ", strip=True))
        role = ""
        details = body.find("span", class_="course-details")
        if details is not None:
            role = normalize_text(details.get_text(" ", strip=True))
        name = full
        if role:
            name = normalize_text(name.replace(role, "").rstrip(" ,"))

        rows.append(
            {
                "code": code,
                "name": name,
                "role": role,
                "links": links_to_csv(unique_anchors(li)),
            }
        )
    return rows


def classify_lang(text: str) -> str:
    low = text.lower()
    swedish_markers = ["å", "ä", "ö", "järnväg", "bro", "förenklad", "dynamisk", "höghastighet", "för", "och"]
    if any(marker in low for marker in swedish_markers):
        return "mixed"
    return "en"


def parse_publications(publications_section: Tag) -> list[dict[str, str]]:
    type_mapping = {
        "Theses": "thesis",
        "Manuscripts": "manuscript",
        "International Journal Papers": "journal",
        "Conference Papers": "conference",
        "Book Chapters": "chapter",
        "Reports, KTH TRITA-BKN": "report_trita",
        "Reports, KTH": "report_kth",
        "Reports, Trafikverket": "report_kth",
    }

    rows = []
    used_ids: Counter[str] = Counter()

    for detail in publications_section.select("details.level-2"):
        summary = detail.find("summary")
        if summary is None:
            continue
        section_name = normalize_text(summary.get_text(" ", strip=True))
        pub_type = type_mapping.get(section_name)
        if not pub_type:
            continue

        for li in list_items(detail):
            body = row_container(li)
            full = normalize_text(body.get_text(" ", strip=True))
            links = links_to_csv(unique_anchors(body))

            parsed_year = ""
            parsed_authors = ""
            parsed_title = full
            m = re.match(r"^(?P<authors>.+?),\s*(?P<year>(?:19|20)\d{2})\.\s*(?P<rest>.+)$", full)
            if m:
                parsed_authors = normalize_text(m.group("authors"))
                parsed_year = normalize_text(m.group("year"))
                parsed_title = normalize_text(m.group("rest"))
            else:
                y = re.search(r"\b((?:19|20)\d{2})\b", full)
                if y:
                    parsed_year = y.group(1)

            italic_texts = [normalize_text(i.get_text(" ", strip=True)) for i in body.find_all("i")]
            italic_texts = [text for text in italic_texts if text]
            venue = " | ".join(dict.fromkeys(italic_texts)) or section_name

            title = parsed_title
            if venue and title.endswith(venue):
                title = normalize_text(title[: -len(venue)].rstrip(" ,.;"))
            title = re.sub(
                r"(?:[\s,.;:()]+(?:download|link|web|papers?|proceedings|karta|google scholar|researchgate|diva))+$",
                "",
                title,
                flags=re.IGNORECASE,
            ).strip(" ,.;")
            if not title:
                title = parsed_title or full

            lang = classify_lang(f"{title} {parsed_authors} {venue}")

            base_id = f"{pub_type}-{parsed_year or 'unknown'}-{slugify(title)[:48]}"
            used_ids[base_id] += 1
            row_id = base_id if used_ids[base_id] == 1 else f"{base_id}-{used_ids[base_id]}"

            rows.append(
                {
                    "id": row_id,
                    "title": title,
                    "year": parsed_year,
                    "type": pub_type,
                    "authors": parsed_authors,
                    "venue": venue,
                    "links": links,
                    "tags": "",
                    "lang": lang,
                }
            )

    rows.sort(key=lambda r: (r["year"], r["id"]), reverse=True)
    return rows


def parse_experimental_links(experimental_section: Tag) -> list[dict[str, str]]:
    rows = []
    for li in experimental_section.select("ul.cv-list > li"):
        date = normalize_text(li.select_one(".cv-year").get_text(" ", strip=True))
        year_match = re.match(r"(\d{4})", date)
        year = year_match.group(1) if year_match else ""
        spans = li.find_all("span")
        body = spans[-1] if spans else li
        rows.append(
            {
                "date": date,
                "year": year,
                "links": links_to_csv(unique_anchors(body)),
                "raw": normalize_text(body.get_text(" ", strip=True)),
            }
        )
    return rows


def sync_experimental(existing_path: Path, source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if existing_path.exists():
        with existing_path.open(encoding="utf-8") as fh:
            existing = list(csv.DictReader(fh))
        if len(existing) == len(source_rows):
            for i, row in enumerate(existing):
                row["date"] = source_rows[i]["date"]
                row["year"] = source_rows[i]["year"]
                row["links"] = source_rows[i]["links"]
            return existing

    fallback = []
    for item in source_rows:
        raw = item["raw"]
        first, _, remainder = raw.partition(".")
        title = normalize_text(first)
        notes = normalize_text(remainder) if remainder else raw

        location = ""
        m = re.search(r"\(([^)]*)\)", title)
        if m:
            location = normalize_text(m.group(1))
        if not location:
            m = re.search(r",\s*([^,]+)$", title)
            if m:
                location = normalize_text(m.group(1))

        fallback.append(
            {
                "date": item["date"],
                "year": item["year"],
                "location": location,
                "title": title,
                "notes": notes,
                "links": item["links"],
            }
        )
    return fallback


def write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in headers})


def fetch_html(source_url: str) -> str:
    req = Request(source_url, headers={"User-Agent": "codex-sync/1.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def run() -> int:
    parser = argparse.ArgumentParser(description="Sync CSV data from source profile HTML")
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--input-html", default="", help="Use local HTML file instead of fetching")
    parser.add_argument(
        "--snapshot-dir",
        default="/tmp/addekth-sync-snapshots",
        help="Directory for timestamped source HTML snapshot",
    )
    parser.add_argument(
        "--report-path",
        default="",
        help="Optional report path; defaults to /tmp/addekth-sync-report-<timestamp>.json",
    )
    args = parser.parse_args()

    if args.input_html:
        html = Path(args.input_html).read_text(encoding="utf-8")
        source_used = args.input_html
    else:
        html = fetch_html(args.source_url)
        source_used = args.source_url

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = Path(args.snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / f"publications_{stamp}.html"
    snapshot_path.write_text(html, encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")
    about = find_level1(soup, "About")
    publications = find_level1(soup, "Publications")
    teaching = find_level1(soup, "Teaching")
    experimental = find_level1(soup, "Experimental testing")

    out_rows = {
        "cv_general.csv": parse_cv_general(soup, about),
        "cv_employments.csv": parse_cv_employments(about),
        "cv_international.csv": parse_cv_international(about),
        "cv_awards.csv": parse_cv_awards(about),
        "projects_commission.csv": parse_projects_commission(about),
        "projects_research.csv": parse_projects_research(about),
        "teaching_phd.csv": parse_teaching_phd(teaching),
        "teaching_master.csv": parse_teaching_master(teaching),
        "teaching_courses.csv": parse_teaching_courses(teaching),
        "publications.csv": parse_publications(publications),
        "external_profiles.csv": parse_external_profiles(soup),
    }

    experimental_source = parse_experimental_links(experimental)
    out_rows["experimental_testing.csv"] = sync_experimental(
        Path("contents/data/experimental_testing.csv"),
        experimental_source,
    )

    headers = {
        "cv_general.csv": ["affiliation", "department", "profile_url"],
        "cv_employments.csv": ["period", "title", "org", "links"],
        "cv_international.csv": ["period", "title", "org", "location", "links", "notes"],
        "cv_awards.csv": ["year", "item", "links"],
        "projects_commission.csv": ["period", "title", "links"],
        "projects_research.csv": ["year", "title", "description", "links"],
        "teaching_phd.csv": ["name", "status", "period", "links"],
        "teaching_master.csv": ["name", "status", "period", "links"],
        "teaching_courses.csv": ["code", "name", "role", "links"],
        "publications.csv": ["id", "title", "year", "type", "authors", "venue", "links", "tags", "lang"],
        "experimental_testing.csv": ["date", "year", "location", "title", "notes", "links"],
        "external_profiles.csv": ["label", "url"],
    }

    for name, rows in out_rows.items():
        write_csv(Path("contents/data") / name, headers[name], rows)

    pub_counts = Counter(r["type"] for r in out_rows["publications.csv"])
    report = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source": source_used,
        "snapshot": str(snapshot_path),
        "row_counts": {name: len(rows) for name, rows in out_rows.items()},
        "publications_by_type": dict(pub_counts),
        "expected_publications_by_type": {
            "thesis": 3,
            "manuscript": 10,
            "journal": 31,
            "conference": 49,
            "chapter": 3,
            "report_trita": 20,
            "report_kth": 125,
        },
    }

    report_path = Path(args.report_path) if args.report_path else Path(f"/tmp/addekth-sync-report-{stamp}.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Source snapshot: {snapshot_path}")
    print(f"Report: {report_path}")
    for name, count in report["row_counts"].items():
        print(f"- {name}: {count}")

    mismatch = []
    for key, expected in report["expected_publications_by_type"].items():
        actual = report["publications_by_type"].get(key, 0)
        if actual != expected:
            mismatch.append((key, expected, actual))
    if mismatch:
        print("WARNING: publication count mismatch detected:")
        for key, expected, actual in mismatch:
            print(f"  {key}: expected={expected} actual={actual}")

    return 0


if __name__ == "__main__":
    sys.exit(run())
