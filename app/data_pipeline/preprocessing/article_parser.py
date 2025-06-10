import os
import re
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
from app.helpers.logger import logger
from app.helpers.processing_helpers import (
    url_to_filename,
    generate_numeric_id,
    normalize_text,
)

async def parse_html(html_path: str, source_url: str) -> list[dict]:
    if "issue" in html_path:
        return await parse_issue_html(html_path, source_url)
    else:
        return await parse_regular_html(html_path, source_url)

async def parse_issue_html(html_path: str, source_url: str) -> list[dict]:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", class_=re.compile(r"prose--styled.*post_postContent"))
    if not content_div:
        return []

    article_slug = url_to_filename(source_url)
    title_tag = soup.find("title")
    title = normalize_text(title_tag.text) if title_tag else "No Title"
    local_html_path = html_path

    results = []
    chunk_index = 1

    current_image = None
    current_subtitle = None
    current_text = []

    def flush_chunk():
        nonlocal chunk_index, current_image, current_subtitle, current_text

        if current_image and current_subtitle and current_text:
            chunk_id = generate_numeric_id(article_slug, chunk_index)
            results.append({
                "id": chunk_id,
                "type": "news_chunk",
                "title": title,
                "subtitle": current_subtitle,
                "content": " ".join(current_text),
                "image_caption": current_image["caption"],
                "metadata": {
                    "article_id": article_slug,
                    "chunk_index": chunk_index,
                    "image_url": current_image["url"],
                    "source_url": source_url,
                    "html_path": local_html_path,
                }
            })

            chunk_index += 1


        current_image = None
        current_subtitle = None
        current_text = []

    for el in content_div.children:
        if not isinstance(el, Tag):
            continue

        if el.name == "hr":
            flush_chunk()

        elif el.name == "figure":
            img = el.find("img")
            if not img:
                continue
            src = img.get("src")
            alt = normalize_text(img.get("alt") or "")
            if not src or not alt or src.startswith("data:"):
                continue

            img_url = urljoin(source_url, src)



            current_image = {
                    "url": img_url,
                    "caption": alt
                }

        elif el.name == "h2":
            subtitle_candidate = normalize_text(el.get_text())
            if subtitle_candidate.lower().strip() != "subscribe to the batch" and subtitle_candidate.lower().strip() != "a message from deeplearning.ai":
                current_subtitle = subtitle_candidate

        elif el.name in ["p", "ul"]:
            text = normalize_text(el.get_text())
            if text and len(text) > 10:
                current_text.append(text)

    flush_chunk()
    return results


async def parse_regular_html(html_path: str, source_url: str) -> list[dict]:


    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    article_slug = url_to_filename(source_url)
    local_html_path = html_path
    chunk_index = 1


    title_tag = soup.find("title")
    title = normalize_text(title_tag.text) if title_tag else "No Title"
    subtitle = title


    image_div = soup.find("div", class_="relative flex items-center w-full max-w-full overflow-hidden aspect-w-16 aspect-h-9")
    current_image = None

    if image_div:
        span_tag = image_div.find("span")
        img_tag = span_tag.find("img") if span_tag else None

        if img_tag:
            alt = normalize_text(img_tag.get("alt") or "")
            src = img_tag.get("src", "")
            img_url = None


            if src and not src.startswith("data:"):
                img_url = urljoin(source_url, src)


            elif img_tag.has_attr("srcset"):
                srcset = img_tag["srcset"]
                first_url = srcset.split(",")[0].split()[0]  # беремо перший URL
                img_url = urljoin(source_url, first_url)


            elif span_tag:
                noscript = span_tag.find_next("noscript")
                if noscript:
                    try:
                        inner = BeautifulSoup(noscript.decode_contents(), "html.parser")
                        fallback_img = inner.find("img")
                        if fallback_img and fallback_img.get("src"):
                            img_url = urljoin(source_url, fallback_img["src"])
                    except Exception as e:
                        logger.error("Failed to parse <noscript>:", e)

            if img_url and alt:

                current_image = {
                        "url": img_url,
                        "caption": alt
                    }


    content_div = soup.find("div", class_="prose--styled justify-self-center post_postContent__wGZtc")
    paragraphs = []

    if content_div:
        for el in content_div.descendants:
            if isinstance(el, Tag) and el.name in ["p", "ul"]:
                text = normalize_text(el.get_text())
                if text and len(text) > 10:
                    paragraphs.append(text)


    if paragraphs:
        return [{
            "id": generate_numeric_id(article_slug, chunk_index),
            "type": "news_chunk",
            "title": title,
            "subtitle": subtitle,
            "content": " ".join(paragraphs),
            "image_caption": current_image["caption"] if current_image else None,
            "metadata": {
                "article_id": article_slug,
                "chunk_index": chunk_index,
                "image_url": current_image["url"] if current_image else None,
                "source_url": source_url,
                "html_path": local_html_path,
            }
        }]
    else:
        logger.warning("No content found in regular HTML.")
        return []