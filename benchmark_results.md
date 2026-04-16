# Catalog Retrieval Benchmark

- Generated: 2026-04-16 17:56:58 KST
- Dataset: built-in tiny sample
- Catalog items: 6
- Queries: 4
- Device: mps
- Top K: 10
- Query instruction: `Given a catalog lookup query, retrieve the matching catalog item.`

## Summary Scores

| model | dim | load_s | doc_s | docs/s | query_batch_s | q_p50_ms | q_p95_ms | search_ms | recall@1 | recall@5 | mrr@10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BAAI/bge-m3 | 1024 | 4.69 | 0.11 | 53.10 | 0.04 | 40.0 | 46.1 | 4.5 | 1.000 | 1.000 | 1.000 |
| Qwen/Qwen3-Embedding-0.6B | 1024 | 2.22 | 0.18 | 33.05 | 0.10 | 60.8 | 65.0 | 0.1 | 1.000 | 1.000 | 1.000 |

## Best By Metric

- Highest recall@1: BAAI/bge-m3 (1.000)
- Highest recall@5: BAAI/bge-m3 (1.000)
- Highest mrr@10: BAAI/bge-m3 (1.000)
- Fastest query p50: BAAI/bge-m3 (40.044ms)
- Fastest query p95: BAAI/bge-m3 (46.089ms)
- Highest document throughput: BAAI/bge-m3 (53.097)

## Example Rankings

### BAAI/bge-m3

- Query: `women medium red shirt`
  Expected: `sku-shirt-red-m`
  Top IDs: `sku-shirt-red-m, sku-shirt-blue-l, sku-jeans-black-32, sku-charger-usbc-65w, sku-phone-case-iphone, sku-bottle-steel-750`
- Query: `usb c charger for laptop`
  Expected: `sku-charger-usbc-65w`
  Top IDs: `sku-charger-usbc-65w, sku-phone-case-iphone, sku-shirt-blue-l, sku-shirt-red-m, sku-bottle-steel-750, sku-jeans-black-32`
- Query: `iphone clear case`
  Expected: `sku-phone-case-iphone`
  Top IDs: `sku-phone-case-iphone, sku-jeans-black-32, sku-bottle-steel-750, sku-charger-usbc-65w, sku-shirt-blue-l, sku-shirt-red-m`

### Qwen/Qwen3-Embedding-0.6B

- Query: `women medium red shirt`
  Expected: `sku-shirt-red-m`
  Top IDs: `sku-shirt-red-m, sku-shirt-blue-l, sku-jeans-black-32, sku-bottle-steel-750, sku-charger-usbc-65w, sku-phone-case-iphone`
- Query: `usb c charger for laptop`
  Expected: `sku-charger-usbc-65w`
  Top IDs: `sku-charger-usbc-65w, sku-jeans-black-32, sku-phone-case-iphone, sku-bottle-steel-750, sku-shirt-red-m, sku-shirt-blue-l`
- Query: `iphone clear case`
  Expected: `sku-phone-case-iphone`
  Top IDs: `sku-phone-case-iphone, sku-bottle-steel-750, sku-charger-usbc-65w, sku-shirt-blue-l, sku-shirt-red-m, sku-jeans-black-32`
