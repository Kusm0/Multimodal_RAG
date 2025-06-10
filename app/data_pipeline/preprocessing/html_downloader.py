import os
import aiohttp
from app.helpers.processing_helpers import url_to_filename


async def download_and_cache_html(url: str, headers_name, html_cache_dir_path) -> str | None:
    filename = url_to_filename(url) + ".html"
    local_path = os.path.join(html_cache_dir_path, filename)

    if os.path.exists(local_path):
        return local_path

    try:
        async with aiohttp.ClientSession(headers=headers_name) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        with open(local_path, "w", encoding="utf-8") as f:
            f.write(html)
        return local_path

    except Exception:
        return None