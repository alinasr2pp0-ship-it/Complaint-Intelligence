"""Chunk size / overlap comparison, backed by throwaway Pinecone namespaces."""
from typing import List

import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.evaluation.retrieval_metrics import evaluate_retrieval
from app.optimization.embedding_comparison import build_temp_retriever

CHUNK_CONFIGS = [
    {"chunk_size": 300, "chunk_overlap": 30},
    {"chunk_size": 600, "chunk_overlap": 100},
]


def run_chunk_comparison(documents_sample: List[Document], test_queries, ground_truth_ids, chunk_configs=None) -> pd.DataFrame:
    chunk_configs = chunk_configs or CHUNK_CONFIGS
    chunk_results = []
    for cfg in chunk_configs:
        splitter = RecursiveCharacterTextSplitter(chunk_size=cfg["chunk_size"], chunk_overlap=cfg["chunk_overlap"])
        chunked_docs = splitter.split_documents(documents_sample)
        temp_retriever = build_temp_retriever(chunked_docs, "all-MiniLM-L6-v2", k=5)
        res = evaluate_retrieval(temp_retriever, test_queries, ground_truth_ids, k=5)
        res.update(cfg)
        chunk_results.append(res)
    return pd.DataFrame(chunk_results)
