from app.adapter.qdrant_embedding_retriever import retrieve_similar_chunks
from app.helpers.prompt_helpers import format_chunks_to_prompt, extract_chunk_metadata

from app.service.llm_answer import generate_answer
from app.service.embedder import get_query_embedding


def call_chain(query: str) -> dict:
    vector_query = get_query_embedding(query)
    hits = retrieve_similar_chunks(vector_query, top_k=3)
    if not hits:
        return {
            "answer": "No relevant context found.",
            "best_image_url": "",
            "best_image_caption": "",
            "chunks_info": []
        }

    context_chunks = format_chunks_to_prompt(hits)
    llm_output = generate_answer(query, context_chunks)
    chunks_info = extract_chunk_metadata(hits)
    return {
        "answer": llm_output.get("answer", ""),
        "best_image_caption": llm_output.get("best_image_caption", ""),
        "best_image_url": llm_output.get("best_image_url", ""),
        "chunks_info": chunks_info
    }

if __name__ == "__main__":
    test_query = "How is AI used in medicine?"

    result = call_chain(test_query)

    print("🧠 Answer:")
    print(result["answer"])

    print("\n🖼️ Best image:")
    print("Caption:", result["best_image_caption"])
    print("URL:", result["best_image_url"])

    print("\n📚 Read more about this topic:")
    for idx, chunk in enumerate(result["chunks_info"], start=1):
        print(f"{idx}. Title: {chunk['title']}")
        print(f"   Source: {chunk['source_url']}")