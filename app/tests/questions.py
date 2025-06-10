from datasets import Dataset
from ragas.llms.openai import OpenAI
from ragas.embeddings.openai import OpenAIEmbeddings
from ragas import evaluate
from ragas.metrics import (
    ContextRecall, ContextPrecision,
    Faithfulness, AnswerRelevancy
)

# 1️⃣ візьмемо n документів (chunk або стаття) як базу
docs = load_some_docs()

questions, gt_answers, model_answers, ctxs = [], [], [], []

llm_qg = OpenAI(model="gpt-4o-mini")          # генератор Q&A
for doc in docs:
    # згенеруємо 1-2 питання й еталонну відповідь
    prompt = f"Сформулюй 2 питаня та короткі відповіді до тексту:\n\n{doc}"
    qa_pairs = llm_qg.generate([prompt])[0].split("\n\n")  # спрощено
    for pair in qa_pairs:
        q, gt = pair.split("Ответ:")
        questions.append(q.strip())
        gt_answers.append([gt.strip()])        # ground-truth як список!

        # 2️⃣ Проганяємо ваш ланцюжок
        out = call_chain(q.strip())
        model_answers.append(out["answer"])
        ctxs.append(out["chunks_info_texts"])  # перетворіть hits на список рядків