import app.config as config
import os, pathlib
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    ContextRecall, ContextPrecision,
    Faithfulness, AnswerRelevancy,
)
from dotenv import load_dotenv

load_dotenv()
assert "OPENAI_API_KEY" in os.environ, "OPENAI_API_KEY is missing!"

CSV_PATH = config.CSV_DATASET_PATH
OUT_DIR = pathlib.Path(config.RAGAS_PATH_RESULT)
ROW_METRICS_CSV = OUT_DIR / "ragas_scored.csv"
SUMMARY_CSV = OUT_DIR / "ragas_summary.csv"
OUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(CSV_PATH, encoding="utf-8")
df["contexts"] = df["context"].apply(lambda x: [str(x)])
hf_ds = Dataset.from_pandas(df[["question", "answer", "ground_truth", "contexts"]])

metrics = [
    ContextRecall(),
    ContextPrecision(),
    Faithfulness(),
    AnswerRelevancy(),
]

scored_ds = evaluate(hf_ds, metrics)

row_df = scored_ds.to_pandas()
row_df.to_csv(ROW_METRICS_CSV, index=False, encoding="utf-8")

metric_cols = [m.name for m in metrics]
agg_df = (
    row_df[metric_cols]
    .mean()
    .round(3)
    .to_frame(name="score")
    .reset_index()
    .rename(columns={"index": "metric"})
)
agg_df.to_csv(SUMMARY_CSV, index=False, encoding="utf-8")

print("Aggregate RAGAS metrics:")
for _, r in agg_df.iterrows():
    print(f"{r.metric:<20}: {r.score:.3f}")

print(f"Row-level metrics  → {ROW_METRICS_CSV}")
print(f"Summary metrics    → {SUMMARY_CSV}")