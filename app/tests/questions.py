import json, time, hashlib, pathlib, random
from typing import List, Dict

import pandas as pd
from tqdm import tqdm
from openai import OpenAI
import app.config as config

from app.adapter.qdrant_embedding_retriever import retrieve_similar_chunks
from app.helpers.prompt_helpers import format_chunks_to_prompt
from app.service.embedder import get_query_embedding
from app.service.llm_answer import generate_answer

JSONL_PATH = config.JSONL_DATASET_PATH
CSV_OUT = config.CSV_DATASET_PATH
N_SAMPLES = 100

client = OpenAI()
CACHE_PATH = pathlib.Path(config.QA_CACHE_PATH)

def ctx_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def load_cache() -> Dict[str, Dict[str, str]]:
    if not CACHE_PATH:
        return {}
    cache = {}
    with CACHE_PATH.open(encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            cache[row["hash"]] = {"question": row["question"], "ground_truth": row["ground_truth"]}
    return cache

def append_to_cache(h: str, qa: Dict[str, str]) -> None:
    with CACHE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"hash": h, **qa}, ensure_ascii=False) + "\n")

def load_contents(path: str, n: int) -> List[str]:
    with open(path, encoding="utf-8") as f:
        contents = [json.loads(l)["content"] for l in f if l.strip()]
    return random.sample(contents, n) if len(contents) > n else contents

SYSTEM_PROMPT = (
    "You are a helpful assistant that writes exam-style questions.\n"
    "Use ONLY the given context to generate:\n"
    " • exactly ONE question in English\n"
    " • exactly ONE correct answer (ground truth) in English\n"
    'Return ONLY valid JSON: {"question": "...", "ground_truth": "..."}'
)

def qa_from_context(ctx: str, model: str = "gpt-4o-mini", max_retries: int = 3) -> Dict[str, str]:
    prompt = f"Context:\n{ctx}\n\nGenerate the question & answer now."
    for attempt in range(max_retries):
        try:
            res = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return json.loads(res.choices[0].message.content)
        except Exception:
            if attempt + 1 == max_retries:
                raise
            time.sleep(2 ** attempt)

def build_qa_pairs(contents: List[str]) -> List[Dict[str, str]]:
    cache = load_cache()
    qa_pairs, new_cnt = [], 0
    for ctx in tqdm(contents, desc="QA generation / cache"):
        h = ctx_hash(ctx)
        if h in cache:
            qa = cache[h]
        else:
            qa = qa_from_context(ctx)
            append_to_cache(h, qa)
            new_cnt += 1
        qa_pairs.append(qa)
    print(f"{new_cnt} new pairs, {len(contents)-new_cnt} from cache")
    return qa_pairs

def save_pairs(csv_path: str, qa_pairs: List[Dict[str, str]]) -> None:
    pd.DataFrame(qa_pairs).to_csv(csv_path, index=False, encoding="utf-8")

def enrich_with_rag(csv_path: str) -> None:
    df = pd.read_csv(csv_path, encoding="utf-8")
    answers, contexts = [], []
    for q in tqdm(df["question"], desc="RAG answering"):
        vec = get_query_embedding(str(q))
        hits = retrieve_similar_chunks(vec, top_k=1)
        ctx_chunks = format_chunks_to_prompt(hits)
        llm_out = generate_answer(str(q), ctx_chunks)
        answers.append(llm_out.get("answer", ""))
        contexts.append(" ".join(ctx_chunks))
    df["answer"], df["context"] = answers, contexts
    df.to_csv(csv_path, index=False, encoding="utf-8")

def make_eval_dataset():
    contents = load_contents(JSONL_PATH, N_SAMPLES)
    qa_pairs = build_qa_pairs(contents)
    save_pairs(CSV_OUT, qa_pairs)
    enrich_with_rag(CSV_OUT)

if __name__ == "__main__":
    make_eval_dataset()
    print(f"Dataset saved to {CSV_OUT} ({N_SAMPLES} rows)")