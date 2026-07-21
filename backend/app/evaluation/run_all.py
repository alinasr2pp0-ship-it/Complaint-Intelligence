"""
Standalone evaluation entry point -- runs qualitative + generation + retrieval
evaluation independently of the API, producing:
    evaluation_report.txt
    metrics_report.csv
    retrieval_evaluation_report.csv

Usage:
    python -m app.evaluation.run_all
"""
from app.config.settings import get_settings
from app.core.logging_config import configure_logging, get_logger
from app.evaluation.generation_metrics import EVAL_DATASET, run_generation_evaluation
from app.evaluation.retrieval_metrics import run_retrieval_evaluation
from app.evaluation.run_qualitative import run_qualitative_eval
from app.rag.chain import get_gemini_client
from app.utils.data_loader import load_dataframe_for_ground_truth
from app.vector_store.store import get_retriever

logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    settings = get_settings()

    logger.info("== Step 1/3: Qualitative test-query run ==")
    run_qualitative_eval(output_path="./evaluation_report.txt")

    logger.info("== Step 2/3: Generation quality (BLEU / ROUGE) ==")
    retriever = get_retriever()
    client = get_gemini_client()
    df_metrics = run_generation_evaluation(retriever, client, settings.GEMINI_MODEL, EVAL_DATASET)
    print(df_metrics.to_markdown(index=False))
    df_metrics.to_csv("metrics_report.csv", index=False)

    logger.info("== Step 3/3: Retrieval quality (Recall@K, MRR) ==")
    df_processed = load_dataframe_for_ground_truth()
    retrieval_report_df = run_retrieval_evaluation(retriever, df_processed, k_values=[1, 3, 5])
    print(retrieval_report_df.to_markdown(index=False))
    retrieval_report_df.to_csv("retrieval_evaluation_report.csv", index=False)

    logger.info("All evaluation reports generated.")


if __name__ == "__main__":
    main()
