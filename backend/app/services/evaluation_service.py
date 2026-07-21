"""Evaluation service -- thin orchestration layer shared by the API and standalone scripts."""
from typing import Any, Dict, List

from app.evaluation.generation_metrics import EVAL_DATASET, run_generation_evaluation
from app.evaluation.retrieval_metrics import TEST_QUERIES, run_retrieval_evaluation
from app.evaluation.run_qualitative import run_qualitative_eval
from app.utils.data_loader import load_dataframe_for_ground_truth
from app.vector_store.store import get_retriever


def run_generation_metrics() -> List[Dict[str, Any]]:
    retriever = get_retriever()
    df = run_generation_evaluation(retriever, EVAL_DATASET)
    return df.to_dict(orient="records")


def run_retrieval_metrics(k_values: List[int] = None) -> List[Dict[str, Any]]:
    retriever = get_retriever()
    df_processed = load_dataframe_for_ground_truth()
    df = run_retrieval_evaluation(retriever, df_processed, k_values=k_values or [1, 3, 5])
    return df.to_dict(orient="records")


def run_qualitative(output_path: str = "./evaluation_report.txt") -> Dict[str, Any]:
    path = run_qualitative_eval(output_path=output_path)
    return {"report_path": path, "num_queries": len(TEST_QUERIES)}
