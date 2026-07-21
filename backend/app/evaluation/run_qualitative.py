"""Qualitative test-query run -- 9 fixed test queries through the live RAG chain."""
from pathlib import Path
from typing import List, Optional

from app.core.logging_config import configure_logging, get_logger
from app.evaluation.retrieval_metrics import TEST_QUERIES
from app.rag.chain import build_rag_chain

logger = get_logger(__name__)


def run_qualitative_eval(output_path: Optional[str] = None, queries: Optional[List[str]] = None) -> str:
    queries = queries or TEST_QUERIES
    output_path = output_path or "./evaluation_report.txt"
    chain = build_rag_chain()

    logger.info("Running RAG pipeline over %s test queries...", len(queries))
    eval_results = []
    for i, query in enumerate(queries, 1):
        logger.info("Answering question %s/%s...", i, len(queries))
        try:
            answer = chain.invoke(query)
        except Exception as e:  # noqa: BLE001
            answer = f"Error generating answer: {str(e)}"
        eval_results.append({"question_number": i, "question": query, "bot_answer": answer})

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n          RAG CHATBOT EVALUATION REPORT          \n" + "=" * 50 + "\n\n")
        for res in eval_results:
            f.write(f"### Q{res['question_number']}: {res['question']}\n")
            f.write(f"\U0001F916 Bot Answer:\n{res['bot_answer']}\n")
            f.write("-" * 50 + "\n\n")

    logger.info("Evaluation complete! Report saved to %s", output_path)
    return output_path


if __name__ == "__main__":
    configure_logging()
    run_qualitative_eval()
