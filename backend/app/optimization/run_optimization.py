"""
Standalone optimization entry point -- runs all four experiments (prompt,
embedding model, chunk size/overlap, retrieval strategy) and writes
`optimization_experiments_report.md`. Independent of the API.

Usage:
    python -m app.optimization.run_optimization
"""
from app.core.logging_config import configure_logging, get_logger
from app.evaluation.generation_metrics import EVAL_DATASET
from app.evaluation.retrieval_metrics import TEST_QUERIES, build_ground_truth_ids, run_retrieval_evaluation
from app.optimization.chunk_comparison import run_chunk_comparison
from app.optimization.embedding_comparison import run_embedding_comparison
from app.optimization.prompt_comparison import run_comparison
from app.optimization.strategy_comparison import run_strategy_comparison
from app.utils.data_loader import load_dataframe_for_ground_truth, load_documents
from app.vector_store.store import get_retriever, get_vector_store

logger = get_logger(__name__)


def main() -> None:
    configure_logging()

    df_processed = load_dataframe_for_ground_truth()
    ground_truth_ids = build_ground_truth_ids(df_processed)
    documents_sample = load_documents(max_rows=500)

    retriever = get_retriever()
    vector_store = get_vector_store()

    logger.info("Retriever k comparison (k=1,3,5)...")
    retrieval_report_df = run_retrieval_evaluation(retriever, df_processed, k_values=[1, 3, 5])

    logger.info("Prompt engineering comparison (v1 vs v2)...")
    comparison_df = run_comparison(retriever, EVAL_DATASET)
    comparison_df.to_csv("prompt_comparison_report.csv", index=False)

    logger.info("Embedding model comparison (MiniLM vs mpnet)...")
    embedding_results_df = run_embedding_comparison(documents_sample, TEST_QUERIES, ground_truth_ids)

    logger.info("Chunk size / overlap comparison...")
    chunk_results_df = run_chunk_comparison(documents_sample, TEST_QUERIES, ground_truth_ids)

    logger.info("Retrieval strategy comparison (similarity vs MMR)...")
    strategy_results_df = run_strategy_comparison(vector_store, TEST_QUERIES, ground_truth_ids)

    with open("optimization_experiments_report.md", "w", encoding="utf-8") as f:
        f.write("# Optimization Experiments\n\n")
        f.write("## Retriever k Comparison\n\n" + retrieval_report_df.to_markdown(index=False) + "\n\n")
        f.write("## Prompt Engineering Comparison\n\n" + comparison_df.to_markdown(index=False) + "\n\n")
        f.write("## Embedding Model Comparison\n\n" + embedding_results_df.to_markdown(index=False) + "\n\n")
        f.write("## Chunk Size / Overlap Comparison\n\n" + chunk_results_df.to_markdown(index=False) + "\n\n")
        f.write("## Retrieval Strategy Comparison\n\n" + strategy_results_df.to_markdown(index=False) + "\n")

    logger.info("All optimization experiments complete. Report saved to optimization_experiments_report.md")


if __name__ == "__main__":
    main()
