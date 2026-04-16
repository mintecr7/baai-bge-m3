# Qwen Embedding API

FastAPI embedding service using `Qwen/Qwen3-Embedding-0.6B` by default.

This model is 1024-dimensional, so it can replace `BAAI/bge-m3` in pgvector
schemas that use `vector(1024)`.

Use `EMBED_MODEL_NAME=BAAI/bge-m3 python3 main.py` to run the BGE-M3 baseline.
Use `EMBED_MODEL_NAME=Qwen/Qwen3-Embedding-4B python3 main.py` only if you also
move to a larger vector schema and can tolerate much slower local inference.

## Query vs Document Embeddings

Catalog documents can use the legacy raw list body:

```bash
curl -sS -X POST http://127.0.0.1:4000/embed/batch \
  -H 'Content-Type: application/json' \
  -d '["ProductName: example device"]'
```

User search queries should use query mode so Qwen receives its retrieval prompt:

```bash
curl -sS -X POST http://127.0.0.1:4000/embed/batch \
  -H 'Content-Type: application/json' \
  -d '{"texts":["portable ultrasound booth"],"mode":"query"}'
```

## Benchmarking

Run the built-in smoke benchmark:

```bash
lang/bin/python benchmark_catalog_retrieval.py
```

Run against your own catalog and labeled queries:

```bash
lang/bin/python benchmark_catalog_retrieval.py \
  --catalog catalog.jsonl \
  --queries queries.jsonl \
  --model BAAI/bge-m3 \
  --model Qwen/Qwen3-Embedding-0.6B
```

Expected query records should include a query field plus `expected_id` or
`expected_ids` so the script can report recall and MRR.
