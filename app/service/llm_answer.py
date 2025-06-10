import app.config as config

import openai
from app.helpers.prompt_helpers import load_system_prompt, parse_llm_response

openai.api_key = config.OPENAI_KEY
OPENAI_LLM = config.OPENAI_LLM_NAME
PROMPT = config.SYSTEM_PROMPT_PATH


def generate_answer(query: str, context_chunks: list[str], model=OPENAI_LLM) -> dict:
    context_text = "\n\n".join(context_chunks)
    system_prompt = load_system_prompt(PROMPT)

    user_prompt = (
        f"Context:\n{context_text}\n\n"
        f"Question: {query}"
    )

    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    return parse_llm_response(content)
