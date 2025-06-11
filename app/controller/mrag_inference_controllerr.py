from app.usecase.mrag_usecase import call_chain


def rag_interface(query: str):
    result = call_chain(query)

    answer = result.get("answer", "")
    image_caption = result.get("best_image_caption", "")
    image_url = result.get("best_image_url", "")
    chunks_info = result.get("chunks_info", [])


    if not (image_url and (image_url.startswith("http://") or image_url.startswith("https://"))):
        image_url = None

    formatted_sources = []
    if chunks_info:
        for idx, chunk in enumerate(chunks_info, start=1):
            title = chunk.get("title", "No Title")
            link = chunk.get("source_url", "")
            if link:
                formatted_sources.append(f"**{idx}.** [{title}]({link})")
            else:
                formatted_sources.append(f"**{idx}.** {title}")

    return answer, image_url, image_caption, "\n\n".join(formatted_sources)