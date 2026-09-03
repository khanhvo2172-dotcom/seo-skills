#!/usr/bin/env python3
"""Extract structural QA data from a streamed TrueProfit live blog page."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag


HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")


def clean_text(node: Tag | None) -> str:
    return node.get_text(" ", strip=True) if node else ""


def hydrate_streamed_components(soup: BeautifulSoup) -> None:
    """Move each streamed S:n payload to its matching B:n placeholder."""
    stages = list(soup.find_all(id=re.compile(r"^S:\d+$")))
    for stage in stages:
        suffix = stage.get("id", "")[2:]
        placeholder = soup.find(id=f"B:{suffix}")
        if not placeholder:
            continue
        for child in list(stage.contents):
            placeholder.insert_before(child.extract())
        placeholder.decompose()
        stage.decompose()


def heading_record(node: Tag | None) -> dict[str, Any] | None:
    if not node or node.name not in HEADING_TAGS:
        return None
    return {"level": int(node.name[1]), "text": clean_text(node)}


def in_scope_tags(soup: BeautifulSoup) -> tuple[list[Tag], Tag, Tag | None]:
    h1 = soup.find("h1")
    if not h1:
        raise RuntimeError("No H1 found")

    bio = h1.find_next("div", class_=lambda c: c and "wrap-bio" in c.split())
    tags = list(soup.find_all(True))
    start = tags.index(h1)
    end = tags.index(bio) if bio in tags else len(tags)
    return tags[start:end], h1, bio


def extract(url: str) -> dict[str, Any]:
    response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    hydrate_streamed_components(soup)

    scope, h1, bio = in_scope_tags(soup)
    scope_ids = {id(tag) for tag in scope}

    headings = [heading_record(tag) for tag in scope if tag.name in HEADING_TAGS]
    headings = [item for item in headings if item]

    quick_recaps = []
    for title in soup.find_all(string=lambda text: text and "quick recap" in text.lower()):
        tag = title.parent
        if not isinstance(tag, Tag) or id(tag) not in scope_ids:
            continue
        box = tag.find_parent("div", class_=lambda c: c and "quickRecap" in c)
        if not box:
            box = tag.parent
        quick_recaps.append(
            {
                "title": clean_text(tag),
                "items": [clean_text(item) for item in box.find_all("li")],
                "previous_heading": heading_record(box.find_previous(HEADING_TAGS)),
                "next_heading": heading_record(box.find_next(HEADING_TAGS)),
            }
        )

    further_reading = []
    for title in soup.find_all(
        string=lambda text: text and text.strip().lower() == "further reading"
    ):
        tag = title.parent
        if not isinstance(tag, Tag) or id(tag) not in scope_ids:
            continue
        box = tag.find_parent("div", class_=lambda c: c and "listOfArticles" in c)
        if not box:
            box = tag.parent
        further_reading.append(
            {
                "links": [
                    {"title": clean_text(link), "url": link.get("href", "")}
                    for link in box.find_all("a")
                ],
                "previous_heading": heading_record(box.find_previous(HEADING_TAGS)),
                "next_heading": heading_record(box.find_next(HEADING_TAGS)),
            }
        )

    faqs = []
    faq_headings = [
        tag
        for tag in scope
        if tag.name == "h2" and "faq" in clean_text(tag).lower()
    ]
    for faq_heading in faq_headings:
        current = faq_heading.find_next()
        while current and current is not bio:
            if isinstance(current, Tag) and current.name == "h2":
                break
            if (
                isinstance(current, Tag)
                and current.name == "h3"
                and "question" in " ".join(current.get("class", [])).lower()
            ):
                wrapper = current.parent
                full = clean_text(wrapper)
                question = clean_text(current)
                answer = full[len(question) :].strip() if full.startswith(question) else full
                faqs.append({"question": question, "answer": answer})
            current = current.find_next()

    missing_alt = []
    for image in scope:
        if image.name != "img":
            continue
        alt = image.get("alt")
        if alt is None or not alt.strip():
            missing_alt.append(
                {
                    "src": image.get("src") or image.get("data-src") or "",
                    "previous_heading": heading_record(image.find_previous(HEADING_TAGS)),
                }
            )

    return {
        "url": url,
        "scope": {"h1": clean_text(h1), "author_bio_found": bio is not None},
        "headings": headings,
        "quick_recaps": quick_recaps,
        "further_reading": further_reading,
        "faqs": faqs,
        "missing_or_empty_alt_images": missing_alt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Live https://trueprofit.io/blog/... URL")
    args = parser.parse_args()
    if not re.match(r"^https://(?:www\.)?trueprofit\.io/blog/", args.url):
        parser.error("URL must be a live trueprofit.io/blog article")

    try:
        data = extract(args.url)
    except Exception as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        return 1

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
