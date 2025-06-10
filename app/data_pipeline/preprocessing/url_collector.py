import re
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from urllib.parse import urlparse, urljoin
import json


def clean_url(url: str) -> str:
    return url.split("?")[0]

async def fetch_html(session, url):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            else:
                return None
    except aiohttp.ClientError:
        return None
    except Exception:
        return None

async def collect_urls_from_tag_page(session, tag_url):
    html = await fetch_html(session, tag_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = None

        if href.startswith("/the-batch/"):
            full_url = urljoin("https://www.deeplearning.ai", href)
        elif href.startswith("https://www.deeplearning.ai/the-batch/"):
            full_url = href
        else:
            continue

        full_url = clean_url(full_url)
        if full_url.count("/") <= 6:
            links.add(full_url)

    return links

def load_excluded_urls_from_jsonl(file_path: str) -> set:
    excluded_urls = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    source_url = data.get('metadata', {}).get('source_url')
                    if source_url:
                        excluded_urls.add(clean_url(source_url))
                except json.JSONDecodeError:
                    pass
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return excluded_urls


async def collect_all_target_urls(headers_name, base_url, tag_names, jsonl_file_path: str = None):
    urls = set()
    async with aiohttp.ClientSession(headers=headers_name) as session:
        for n in range(1, 305):
            urls.add(clean_url(f"{base_url}issue-{n}/"))

        tasks = []
        for tag in tag_names:
            tag_url = f"{base_url}tag/{tag}"
            tasks.append(collect_urls_from_tag_page(session, tag_url))

        tag_results = await asyncio.gather(*tasks)
        for tag_links in tag_results:
            urls.update(tag_links)

    if jsonl_file_path:
        excluded_urls = load_excluded_urls_from_jsonl(jsonl_file_path)
        urls = urls - excluded_urls

    return urls