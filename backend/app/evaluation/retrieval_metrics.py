from typing import Dict, List, Set

import pandas as pd

TEST_QUERIES: List[str] = [
    "I have an issue with U.S. BANCORP regarding my mother's closed credit card account which had a credit balance of $420.00, and I have power of attorney. What happened in this specific complaint?",
    "What are the details of the complaint filed against I.C. System, Inc. regarding an attempt to collect a debt not owed due to identity theft hindering the consumer's ability to close a loan?",
    "Search the data for a mortgage-related issue involving Shellpoint Partners, LLC where the servicing remained with Newrez LLC. What was the core problem?",
    "If a consumer complains that Wells Fargo is incorrectly reporting a checking/savings account as a credit card on their credit profile, what is the typical company response or resolution outcome for such an issue?",
    "Based on the dataset, when consumers file complaints against credit reporting agencies like TransUnion for 'Improper use of your report', what legal sections or standard explanations do companies usually provide in their response?",
    "Summarize the primary reasons why consumers file complaints regarding 'Attempts to collect debt not owed' within this dataset sample. What is the most common underlying cause?",
    "What are the main arguments consumers use when accusing credit reporting companies (like Equifax or TransUnion) of violating their privacy rights under 15 U.S.C. 1681 Section 602?",
    "I went through my credit records and noticed fraudulent accounts that do not belong to me are still reposting on my file even after I disputed them. What insights or patterns do similar complaints in the database show regarding this situation?",
    "Are there any complaints in the dataset where credit bureaus or companies refuse to process disputes because they suspect it was filed by a third-party or a credit repair company rather than the consumer themselves?",
]

RETRIEVAL_GROUND_TRUTH: List[Dict[str, str]] = [
    {"company_contains": "U.S. BANCORP"},
    {"company_contains": "I.C. SYSTEM"},
    {"company_contains": "SHELLPOINT"},
    {"company_contains": "WELLS FARGO", "issue_contains": "credit card"},
    {"company_contains": "TRANSUNION", "issue_contains": "improper use"},
    {"issue_contains": "attempts to collect debt not owed"},
    {"company_contains": "EQUIFAX|TRANSUNION", "issue_contains": "privacy"},
    {"issue_contains": "fraud", "narrative_contains": "dispute"},
    {"issue_contains": "dispute", "narrative_contains": "third party|credit repair"},
]


def get_relevant_ids(df_source: pd.DataFrame, filt: Dict[str, str]) -> Set[str]:
    mask = pd.Series(True, index=df_source.index)
    if "company_contains" in filt:
        mask &= df_source["Company"].astype(str).str.contains(filt["company_contains"], case=False, na=False, regex=True)
    if "issue_contains" in filt:
        mask &= df_source["Issue"].astype(str).str.contains(filt["issue_contains"], case=False, na=False, regex=True)
    if "narrative_contains" in filt:
        mask &= df_source["narrative_clean"].astype(str).str.contains(filt["narrative_contains"], case=False, na=False, regex=True)
    return set(df_source.loc[mask, "Complaint ID"].astype(str))


def build_ground_truth_ids(df_processed: pd.DataFrame, filters: List[Dict[str, str]] = None) -> List[Set[str]]:
    filters = filters or RETRIEVAL_GROUND_TRUTH
    return [get_relevant_ids(df_processed, f) for f in filters]


def evaluate_retrieval(retriever, queries: List[str], ground_truth_ids: List[Set[str]], k: int = 5) -> Dict:
    recalls, reciprocal_ranks = [], []
    for query, rel_ids in zip(queries, ground_truth_ids):
        if not rel_ids:
            continue
        docs = retriever.vectorstore.similarity_search(query, k=k)
        retrieved_ids = [d.metadata.get("complaint_id") for d in docs[:k]]
        hits = [1 if rid in rel_ids else 0 for rid in retrieved_ids]
        recalls.append(sum(hits) / len(rel_ids))
        rr = 0.0
        for rank, is_hit in enumerate(hits, 1):
            if is_hit:
                rr = 1 / rank
                break
        reciprocal_ranks.append(rr)
    return {
        "k": k,
        "num_queries_evaluated": len(recalls),
        "Recall@K": round(sum(recalls) / len(recalls), 3) if recalls else 0.0,
        "MRR": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 3) if reciprocal_ranks else 0.0,
    }


def run_retrieval_evaluation(retriever, df_processed: pd.DataFrame, k_values: List[int] = None) -> pd.DataFrame:
    k_values = k_values or [1, 3, 5]
    ground_truth_ids = build_ground_truth_ids(df_processed)
    rows = [evaluate_retrieval(retriever, TEST_QUERIES, ground_truth_ids, k=k) for k in k_values]
    return pd.DataFrame(rows)
