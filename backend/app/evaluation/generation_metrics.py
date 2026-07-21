"""Generation-quality evaluation (ROUGE-1 / ROUGE-L / smoothed sentence-BLEU)."""
import time
from typing import Tuple

import pandas as pd
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer

_scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
_smoothing = SmoothingFunction().method1

EVAL_DATASET = [
    {
        "question": "What are the details of the complaint filed against I.C. System, Inc. regarding an attempt to collect a debt not owed due to identity theft hindering the consumer's ability to close a loan?",
        "ground_truth": "I.C. System, Inc. attempted to collect a debt that the consumer did not owe because it resulted from identity theft. This fraudulent debt severely hindered the consumer's ability to secure or close a loan.",
    },
    {
        "question": "If a consumer complains that Wells Fargo is incorrectly reporting a checking/savings account as a credit card on their credit profile, what is the typical company response or resolution outcome for such an issue?",
        "ground_truth": "Wells Fargo typically responds by reviewing the credit profile reporting error, updating the status, and confirming whether the account is correctly categorized as a banking relationship or closing/correcting the record.",
    },
    {
        "question": "Summarize the primary reasons why consumers file complaints regarding 'Attempts to collect debt not owed' within this dataset sample. What is the most common underlying cause?",
        "ground_truth": "The primary reasons include identity theft, medical bills already paid, or misidentified accounts. The most common underlying cause is outdated or incorrect information in collection agency records.",
    },
]


def calculate_metrics(bot_ans: str, ground_truth: str) -> Tuple[float, float, float]:
    rouge_results = _scorer.score(ground_truth, bot_ans)
    r1, rl = rouge_results["rouge1"].fmeasure, rouge_results["rougeL"].fmeasure
    bleu = sentence_bleu(
        [ground_truth.lower().split()],
        bot_ans.lower().split(),
        weights=(0.5, 0.5, 0, 0),
        smoothing_function=_smoothing,
    )
    return round(r1, 3), round(rl, 3), round(bleu, 3)


def run_generation_evaluation(retriever, client, gemini_model: str, eval_dataset=None) -> "pd.DataFrame":
    from app.rag.prompts import get_prompt

    eval_dataset = eval_dataset or EVAL_DATASET
    results_list = []
    for idx, item in enumerate(eval_dataset, 1):
        q, gt = item["question"], item["ground_truth"]
        start_time = time.time()
        docs = retriever.invoke(q)
        context = "\n\n".join(doc.page_content for doc in docs)
        full_prompt = get_prompt(context, q, version="v1")
        response = client.models.generate_content(model=gemini_model, contents=full_prompt)
        latency = round(time.time() - start_time, 2)
        r1, rl, bleu = calculate_metrics(response.text, gt)
        results_list.append({"Q": idx, "Latency(s)": latency, "ROUGE-1": r1, "ROUGE-L": rl, "BLEU": bleu})
    return pd.DataFrame(results_list)
