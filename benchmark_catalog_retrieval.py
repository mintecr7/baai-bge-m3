import argparse
import csv
import gc
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
from sentence_transformers import SentenceTransformer


DEFAULT_MODELS = ["BAAI/bge-m3", "Qwen/Qwen3-Embedding-0.6B"]
DEFAULT_QUERY_INSTRUCTION = "Given a catalog lookup query, retrieve the matching catalog item."

SAMPLE_CATALOG = [
    {"id": "sku-shirt-red-m", "text": "red cotton t-shirt for women size medium"},
    {"id": "sku-shirt-blue-l", "text": "blue cotton t-shirt for men size large"},
    {"id": "sku-jeans-black-32", "text": "black denim jeans waist 32 slim fit"},
    {"id": "sku-phone-case-iphone", "text": "clear protective case for iPhone 15"},
    {"id": "sku-charger-usbc-65w", "text": "65 watt USB-C laptop and phone charger"},
    {"id": "sku-bottle-steel-750", "text": "stainless steel insulated water bottle 750 ml"},
]

SAMPLE_QUERIES = [
    {"query": "women medium red shirt", "expected_id": "sku-shirt-red-m"},
    {"query": "usb c charger for laptop", "expected_id": "sku-charger-usbc-65w"},
    {"query": "iphone clear case", "expected_id": "sku-phone-case-iphone"},
    {"query": "black slim 32 jeans", "expected_id": "sku-jeans-black-32"},
]


@dataclass
class QueryCase:
    text: str
    expected_ids: List[str]


def read_records(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        records = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("records", "items", "catalog", "queries", "data"):
                if isinstance(data.get(key), list):
                    return data[key]
        raise ValueError(f"{path} must contain a JSON list or a dict with a records/items/catalog/queries/data list")

    if suffix in (".csv", ".tsv"):
        dialect = "excel-tab" if suffix == ".tsv" else "excel"
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f, dialect=dialect))

    raise ValueError(f"Unsupported file type for {path}; use jsonl, json, csv, or tsv")


def first_present(record: Dict[str, Any], names: Sequence[str]) -> Optional[str]:
    for name in names:
        value = record.get(name)
        if value not in (None, ""):
            return str(value)
    return None


def record_text(record: Dict[str, Any], text_field: Optional[str], skip_fields: Sequence[str]) -> str:
    if text_field:
        return str(record.get(text_field, ""))
    value = first_present(record, ("text", "content", "description", "name", "title"))
    if value is not None:
        return value

    pieces = []
    skip = set(skip_fields)
    for key, value in record.items():
        if key in skip or value in (None, ""):
            continue
        pieces.append(f"{key}: {value}")
    return " | ".join(pieces)


def parse_expected_ids(value: Any) -> List[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v not in (None, "")]
    text = str(value)
    for sep in ("|", ";", ","):
        if sep in text:
            return [part.strip() for part in text.split(sep) if part.strip()]
    return [text.strip()] if text.strip() else []


def load_catalog(args: argparse.Namespace) -> Tuple[List[str], List[str], bool]:
    records = SAMPLE_CATALOG if args.catalog is None else read_records(Path(args.catalog))
    if args.limit_catalog:
        records = records[: args.limit_catalog]

    id_fields = [args.id_field] if args.id_field else []
    id_fields.extend(["id", "sku", "product_id", "company_id", "item_id"])

    ids: List[str] = []
    texts: List[str] = []
    for idx, record in enumerate(records):
        doc_id = first_present(record, id_fields)
        ids.append(doc_id or str(idx))
        texts.append(record_text(record, args.text_field, ("id", "sku", "product_id", "item_id")))
    return ids, texts, args.catalog is None


def load_queries(args: argparse.Namespace) -> Tuple[List[QueryCase], bool]:
    records = SAMPLE_QUERIES if args.queries is None else read_records(Path(args.queries))
    if args.limit_queries:
        records = records[: args.limit_queries]

    queries: List[QueryCase] = []
    for record in records:
        if args.query_field:
            text = record_text(record, args.query_field, ("expected_id", "expected_ids", "relevant_id", "relevant_ids"))
        else:
            text = first_present(record, ("query", "text", "question", "message")) or record_text(
                record,
                None,
                ("expected_id", "expected_ids", "relevant_id", "relevant_ids"),
            )
        expected_value = None
        if args.expected_field:
            expected_value = record.get(args.expected_field)
        else:
            for field in ("expected_ids", "expected_id", "relevant_ids", "relevant_id", "id"):
                if field in record:
                    expected_value = record[field]
                    break
        queries.append(QueryCase(text=text, expected_ids=parse_expected_ids(expected_value)))
    return queries, args.queries is None


def resolve_device(device: str) -> str:
    if device != "auto":
        return device
    return "mps" if torch.backends.mps.is_available() else "cpu"


def clear_memory(device: str) -> None:
    if device == "mps" and torch.backends.mps.is_available():
        try:
            torch.mps.empty_cache()
        except Exception:
            pass
    gc.collect()


def encode_kwargs(model_name: str, mode: str, query_instruction: str) -> Dict[str, str]:
    if mode == "query" and "qwen" in model_name.lower():
        return {"prompt": f"Instruct: {query_instruction}\nQuery:"}
    return {}


def encode_texts(
    model: SentenceTransformer,
    model_name: str,
    texts: Sequence[str],
    mode: str,
    batch_size: int,
    query_instruction: str,
) -> np.ndarray:
    if not texts:
        return np.empty((0, 0), dtype=np.float32)
    with torch.inference_mode():
        vectors = model.encode(
            list(texts),
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
            **encode_kwargs(model_name, mode, query_instruction),
        )
    return np.asarray(vectors, dtype=np.float32)


def topk_search(query_vectors: np.ndarray, doc_vectors: np.ndarray, top_k: int) -> np.ndarray:
    if len(doc_vectors) == 0 or len(query_vectors) == 0:
        return np.empty((0, 0), dtype=np.int64)
    k = min(top_k, len(doc_vectors))
    scores = query_vectors @ doc_vectors.T
    unsorted = np.argpartition(-scores, kth=k - 1, axis=1)[:, :k]
    unsorted_scores = np.take_along_axis(scores, unsorted, axis=1)
    order = np.argsort(-unsorted_scores, axis=1)
    return np.take_along_axis(unsorted, order, axis=1)


def percentile_ms(values: Sequence[float], percentile: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(np.asarray(values) * 1000.0, percentile))


def retrieval_metrics(top_indices: np.ndarray, queries: Sequence[QueryCase], doc_ids: Sequence[str]) -> Dict[str, float]:
    labeled = [(idx, set(q.expected_ids)) for idx, q in enumerate(queries) if q.expected_ids]
    if not labeled:
        return {}

    metrics: Dict[str, float] = {}
    for k in (1, 5, 10):
        recalls = []
        hits = []
        for query_idx, expected in labeled:
            top_ids = {doc_ids[i] for i in top_indices[query_idx, : min(k, top_indices.shape[1])]}
            hit_count = len(top_ids & expected)
            recalls.append(hit_count / len(expected))
            hits.append(1.0 if hit_count else 0.0)
        metrics[f"recall@{k}"] = float(np.mean(recalls))
        metrics[f"hit@{k}"] = float(np.mean(hits))

    reciprocal_ranks = []
    for query_idx, expected in labeled:
        rr = 0.0
        for rank, doc_idx in enumerate(top_indices[query_idx, : min(10, top_indices.shape[1])], start=1):
            if doc_ids[doc_idx] in expected:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)
    metrics["mrr@10"] = float(np.mean(reciprocal_ranks))
    metrics["labeled_queries"] = float(len(labeled))
    return metrics


def run_model(
    model_name: str,
    args: argparse.Namespace,
    doc_ids: Sequence[str],
    doc_texts: Sequence[str],
    queries: Sequence[QueryCase],
) -> Dict[str, Any]:
    device = resolve_device(args.device)
    clear_memory(device)

    started = time.perf_counter()
    model = SentenceTransformer(
        model_name,
        device=device,
        trust_remote_code=True,
        local_files_only=not args.allow_download,
    )
    model.eval()
    load_s = time.perf_counter() - started

    encode_texts(model, model_name, ["warmup"], "doc", 1, args.query_instruction)
    encode_texts(model, model_name, ["warmup"], "query", 1, args.query_instruction)

    started = time.perf_counter()
    doc_vectors = encode_texts(model, model_name, doc_texts, "doc", args.doc_batch_size, args.query_instruction)
    doc_embed_s = time.perf_counter() - started

    query_texts = [q.text for q in queries]
    started = time.perf_counter()
    query_vectors = encode_texts(model, model_name, query_texts, "query", args.query_batch_size, args.query_instruction)
    query_batch_s = time.perf_counter() - started

    latency_times = []
    latency_texts = query_texts[: args.latency_samples] or ["warmup"]
    for _ in range(args.query_repeats):
        for text in latency_texts:
            started = time.perf_counter()
            encode_texts(model, model_name, [text], "query", 1, args.query_instruction)
            latency_times.append(time.perf_counter() - started)

    started = time.perf_counter()
    top_indices = topk_search(query_vectors, doc_vectors, args.top_k)
    search_s = time.perf_counter() - started

    result: Dict[str, Any] = {
        "model": model_name,
        "device": device,
        "dimension": int(doc_vectors.shape[1]) if doc_vectors.ndim == 2 and len(doc_vectors) else model.get_sentence_embedding_dimension(),
        "load_s": load_s,
        "catalog_count": len(doc_texts),
        "query_count": len(query_texts),
        "doc_embed_s": doc_embed_s,
        "docs_per_s": len(doc_texts) / doc_embed_s if doc_embed_s else 0.0,
        "query_batch_s": query_batch_s,
        "query_p50_ms": percentile_ms(latency_times, 50),
        "query_p95_ms": percentile_ms(latency_times, 95),
        "search_ms": search_s * 1000.0,
        "top_examples": [],
    }
    result.update(retrieval_metrics(top_indices, queries, doc_ids))

    for query_idx, query in enumerate(queries[: args.show_examples]):
        result["top_examples"].append(
            {
                "query": query.text,
                "expected_ids": query.expected_ids,
                "top_ids": [doc_ids[i] for i in top_indices[query_idx, : min(args.top_k, top_indices.shape[1])]],
            }
        )

    del model
    clear_memory(device)
    return result


def print_table(results: Sequence[Dict[str, Any]]) -> None:
    headers = [
        "model",
        "dim",
        "load_s",
        "doc_s",
        "docs/s",
        "query_batch_s",
        "q_p50_ms",
        "q_p95_ms",
        "search_ms",
        "recall@1",
        "recall@5",
        "mrr@10",
    ]
    rows = []
    for result in results:
        rows.append(
            [
                result["model"],
                str(result["dimension"]),
                f"{result['load_s']:.2f}",
                f"{result['doc_embed_s']:.2f}",
                f"{result['docs_per_s']:.2f}",
                f"{result['query_batch_s']:.2f}",
                f"{result['query_p50_ms']:.1f}",
                f"{result['query_p95_ms']:.1f}",
                f"{result['search_ms']:.1f}",
                f"{result['recall@1']:.3f}" if "recall@1" in result else "n/a",
                f"{result['recall@5']:.3f}" if "recall@5" in result else "n/a",
                f"{result['mrr@10']:.3f}" if "mrr@10" in result else "n/a",
            ]
        )
    widths = [max(len(header), *(len(row[idx]) for row in rows)) for idx, header in enumerate(headers)]
    print("  ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers)))
    print("  ".join("-" * widths[idx] for idx in range(len(headers))))
    for row in rows:
        print("  ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers))))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare embedding models for catalog retrieval.")
    parser.add_argument("--catalog", help="Catalog records as jsonl, json, csv, or tsv.")
    parser.add_argument("--queries", help="Query records as jsonl, json, csv, or tsv.")
    parser.add_argument("--model", action="append", dest="models", help="Model to benchmark. Repeatable.")
    parser.add_argument("--id-field", help="Catalog id field. Auto-detects id/sku/product_id/item_id when omitted.")
    parser.add_argument("--text-field", help="Catalog text field. Auto-detects text/content/description/name/title when omitted.")
    parser.add_argument("--query-field", help="Query text field. Defaults to query.")
    parser.add_argument("--expected-field", help="Expected/relevant id field for quality metrics.")
    parser.add_argument("--device", default="auto", choices=("auto", "mps", "cpu"), help="Device to use.")
    parser.add_argument("--doc-batch-size", type=int, default=16)
    parser.add_argument("--query-batch-size", type=int, default=8)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--limit-catalog", type=int)
    parser.add_argument("--limit-queries", type=int)
    parser.add_argument("--latency-samples", type=int, default=20)
    parser.add_argument("--query-repeats", type=int, default=1)
    parser.add_argument("--show-examples", type=int, default=3)
    parser.add_argument("--query-instruction", default=DEFAULT_QUERY_INSTRUCTION)
    parser.add_argument("--allow-download", action="store_true", help="Allow Hugging Face downloads if a model is not cached.")
    parser.add_argument("--output-json", help="Write detailed benchmark results to this path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.models = args.models or DEFAULT_MODELS

    if torch.backends.mps.is_available():
        torch.backends.mps.enable_fallback = True

    doc_ids, doc_texts, sample_catalog = load_catalog(args)
    queries, sample_queries = load_queries(args)
    if sample_catalog or sample_queries:
        print("Using the built-in tiny sample. Pass --catalog and --queries for a real catalog benchmark.")

    results = []
    for model_name in args.models:
        print(f"\nBenchmarking {model_name}...")
        results.append(run_model(model_name, args, doc_ids, doc_texts, queries))

    print("\nSummary")
    print_table(results)

    for result in results:
        if not result["top_examples"]:
            continue
        print(f"\nExamples for {result['model']}")
        for example in result["top_examples"]:
            print(f"- query={example['query']!r} expected={example['expected_ids']} top={example['top_ids']}")

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nWrote {args.output_json}")


if __name__ == "__main__":
    main()
