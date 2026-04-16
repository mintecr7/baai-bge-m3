# Catalog Retrieval Benchmark

- Generated: 2026-04-16 18:15:27 KST
- Dataset: custom files
- Catalog source: `benchmark_data/localhost_catalog.jsonl`
- Query source: `benchmark_data/localhost_queries.jsonl`
- Catalog items: 1152
- Queries: 100
- Device: mps
- Top K: 50
- Max doc chars: 1200
- Max query chars: 400
- Query instruction: `Given a catalog lookup query, retrieve the matching catalog item.`

## Summary Scores

| model | dim | load_s | doc_s | docs/s | query_batch_s | q_p50_ms | q_p95_ms | search_ms | recall@1 | recall@5 | mrr@10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BAAI/bge-m3 | 1024 | 3.95 | 30.67 | 37.56 | 1.19 | 47.1 | 53.7 | 1.6 | 0.910 | 0.970 | 0.929 |
| Qwen/Qwen3-Embedding-0.6B | 1024 | 2.64 | 67.83 | 16.98 | 3.30 | 81.4 | 98.8 | 5.3 | 0.950 | 0.990 | 0.964 |

## Best By Metric

- Highest recall@1: Qwen/Qwen3-Embedding-0.6B (0.950)
- Highest recall@5: Qwen/Qwen3-Embedding-0.6B (0.990)
- Highest mrr@10: Qwen/Qwen3-Embedding-0.6B (0.964)
- Fastest query p50: BAAI/bge-m3 (47.065ms)
- Fastest query p95: BAAI/bge-m3 (53.731ms)
- Highest document throughput: BAAI/bge-m3 (37.560)

## Example Rankings

### BAAI/bge-m3

- Query: `find company kssungsun@gmail.com Dermatology and Beauty Care`
  Expected: `company:b8783940-9db0-4311-9c61-e99cb97de91c`
  Top IDs: `company:b8783940-9db0-4311-9c61-e99cb97de91c, company:5a017142-4f7c-4aa6-8af3-82a4da0a9f1c, company:76767565-bb6f-4955-b7ad-a2f011641099, company:89140016-4c3b-4e8d-b922-ac86a624f957, company:be729f12-75a4-4bd7-ae03-ac315bc3a168, company:65c52a63-6ee1-4a70-aa6d-3e54b160df4f, company:d9595529-1e35-4718-8f0e-3973fac9bd00, company:a68a099a-e4ec-4742-b4fa-5ae0df2a8304, product:c09e8248-eec4-4946-ba13-303375306412, product:dd9402cf-68b5-466b-b449-61d8705435c9`
- Query: `find company Twohands Interactive Inc. Medical IT Systems/Solutions / Physical Therapy/Rehabilitation/Prehabilitation`
  Expected: `company:223758a2-dd4e-4816-9f53-af5073c7d7a0`
  Top IDs: `company:223758a2-dd4e-4816-9f53-af5073c7d7a0, company:49ba3b5c-95d0-4d64-bc54-946faefe0b13, company:eaa36ab7-dee5-4ef2-9c6a-c9f073f4ce32, company:02a1472b-0bf7-4288-b773-71924c1c78f4, company:62cae47c-25ea-4a64-ba18-ec3eee464d96, company:da8b66a3-1e21-4e14-bdd3-fb9ecb4508cc, company:30ff2d26-6bfb-4d86-934c-68bf79fd269c, company:a949c29e-12cd-4ed6-ab61-cc01f5f59929, company:cacc2571-9843-47b6-a5c6-40dcabafb1c1, company:5a543f7b-ba7c-4d5c-8f37-dff078e48df1`
- Query: `find company Kangwon National University RISE Project Group Bio/Pharmaceutical Devices / Medical IT Systems/Solutions / Clinical Examination and Diagnostics C604`
  Expected: `company:a1fd5777-7732-4e45-9036-11be529ec8bb`
  Top IDs: `company:a1fd5777-7732-4e45-9036-11be529ec8bb, company:12760401-e864-402c-895e-c895af4dff4f, company:223758a2-dd4e-4816-9f53-af5073c7d7a0, company:570ae9d1-7020-4880-883a-b4c5824aac13, company:30ff2d26-6bfb-4d86-934c-68bf79fd269c, company:5a543f7b-ba7c-4d5c-8f37-dff078e48df1, company:7025e4d3-e8eb-4ba5-84d1-b532711595c2, company:a949c29e-12cd-4ed6-ab61-cc01f5f59929, company:b14a6e38-0dbc-460b-a25a-3a8218c73ed6, company:cacc2571-9843-47b6-a5c6-40dcabafb1c1`
- Query: `find company JS TECHWIN Medical Imaging Diagnostics B610`
  Expected: `company:3d5173a7-5ef9-42d6-af90-fc67050e931b`
  Top IDs: `company:3d5173a7-5ef9-42d6-af90-fc67050e931b, product:a4875b37-ceeb-4764-84bf-67e2b8dd2801, product:f9c8b8cb-75de-430d-be0d-a0713bee1599, product:9cb26465-d6aa-4ec1-84d6-8605f0688590, product:71610259-4fd9-4826-975a-6ddaf89353da, product:c4598969-6d15-4192-b0c0-b331ad06e2fa, product:df8d0461-4b85-4550-a3a7-6f7f17094fe6, company:30ff2d26-6bfb-4d86-934c-68bf79fd269c, company:12760401-e864-402c-895e-c895af4dff4f, company:a68a099a-e4ec-4742-b4fa-5ae0df2a8304`
- Query: `find company EROP Co., Ltd. Bio/Pharmaceutical Devices / Medical Device Components and Materials / Operating Equipment B610`
  Expected: `company:12760401-e864-402c-895e-c895af4dff4f`
  Top IDs: `company:12760401-e864-402c-895e-c895af4dff4f, company:7a836daf-d20c-46aa-b754-7940c792fc88, company:a856650a-fd1a-4997-ad77-fd79fba6c714, company:33a2f9bd-ff55-40cc-8b16-c21ce5e6cd4c, company:a68a099a-e4ec-4742-b4fa-5ae0df2a8304, company:a1fd5777-7732-4e45-9036-11be529ec8bb, company:c61dc3ad-9411-40f8-abd9-c8e355aa05a7, company:96dd6180-b868-44cf-82fd-035c8d9d9a42, company:d51e76f6-6744-446f-a0ca-5d73db4409e3, product:00d168d7-7883-4780-a1cd-5f2d00c65155`

### Qwen/Qwen3-Embedding-0.6B

- Query: `find company kssungsun@gmail.com Dermatology and Beauty Care`
  Expected: `company:b8783940-9db0-4311-9c61-e99cb97de91c`
  Top IDs: `company:b8783940-9db0-4311-9c61-e99cb97de91c, company:be729f12-75a4-4bd7-ae03-ac315bc3a168, company:76767565-bb6f-4955-b7ad-a2f011641099, company:5a017142-4f7c-4aa6-8af3-82a4da0a9f1c, company:89140016-4c3b-4e8d-b922-ac86a624f957, company:d9595529-1e35-4718-8f0e-3973fac9bd00, company:65c52a63-6ee1-4a70-aa6d-3e54b160df4f, product:7a765930-b579-4d9e-9185-1660ff687dfe, product:dd9402cf-68b5-466b-b449-61d8705435c9, product:31821b34-a798-4e67-8810-ece87506fc25`
- Query: `find company Twohands Interactive Inc. Medical IT Systems/Solutions / Physical Therapy/Rehabilitation/Prehabilitation`
  Expected: `company:223758a2-dd4e-4816-9f53-af5073c7d7a0`
  Top IDs: `company:223758a2-dd4e-4816-9f53-af5073c7d7a0, company:eaa36ab7-dee5-4ef2-9c6a-c9f073f4ce32, company:49ba3b5c-95d0-4d64-bc54-946faefe0b13, company:02a1472b-0bf7-4288-b773-71924c1c78f4, company:62cae47c-25ea-4a64-ba18-ec3eee464d96, company:da8b66a3-1e21-4e14-bdd3-fb9ecb4508cc, company:30ff2d26-6bfb-4d86-934c-68bf79fd269c, company:cacc2571-9843-47b6-a5c6-40dcabafb1c1, company:a949c29e-12cd-4ed6-ab61-cc01f5f59929, company:7025e4d3-e8eb-4ba5-84d1-b532711595c2`
- Query: `find company Kangwon National University RISE Project Group Bio/Pharmaceutical Devices / Medical IT Systems/Solutions / Clinical Examination and Diagnostics C604`
  Expected: `company:a1fd5777-7732-4e45-9036-11be529ec8bb`
  Top IDs: `company:a1fd5777-7732-4e45-9036-11be529ec8bb, company:33a2f9bd-ff55-40cc-8b16-c21ce5e6cd4c, company:12760401-e864-402c-895e-c895af4dff4f, company:30ff2d26-6bfb-4d86-934c-68bf79fd269c, company:8a2f1834-39d9-40d3-9dc6-5a9f721bd02b, company:3a8e8593-3bd3-4e31-9fd9-0eb60194cc03, company:815b0514-23a9-4740-bed5-3dc2b48f89d2, company:b14a6e38-0dbc-460b-a25a-3a8218c73ed6, company:95007577-2261-4880-91f8-665dea20255b, company:a856650a-fd1a-4997-ad77-fd79fba6c714`
- Query: `find company JS TECHWIN Medical Imaging Diagnostics B610`
  Expected: `company:3d5173a7-5ef9-42d6-af90-fc67050e931b`
  Top IDs: `company:3d5173a7-5ef9-42d6-af90-fc67050e931b, product:f9c8b8cb-75de-430d-be0d-a0713bee1599, product:a4875b37-ceeb-4764-84bf-67e2b8dd2801, product:9cb26465-d6aa-4ec1-84d6-8605f0688590, product:c4598969-6d15-4192-b0c0-b331ad06e2fa, product:71610259-4fd9-4826-975a-6ddaf89353da, company:30ff2d26-6bfb-4d86-934c-68bf79fd269c, company:a856650a-fd1a-4997-ad77-fd79fba6c714, product:24bdeaec-9125-447a-8c71-9e0a006c0b40, product:a9c63608-081d-42bc-b625-d4698a0dd473`
- Query: `find company EROP Co., Ltd. Bio/Pharmaceutical Devices / Medical Device Components and Materials / Operating Equipment B610`
  Expected: `company:12760401-e864-402c-895e-c895af4dff4f`
  Top IDs: `company:12760401-e864-402c-895e-c895af4dff4f, company:33a2f9bd-ff55-40cc-8b16-c21ce5e6cd4c, company:96dd6180-b868-44cf-82fd-035c8d9d9a42, company:c61dc3ad-9411-40f8-abd9-c8e355aa05a7, company:a68a099a-e4ec-4742-b4fa-5ae0df2a8304, company:95007577-2261-4880-91f8-665dea20255b, product:a8a8dab5-b6e8-4036-aed0-7e00cb30c851, product:00d168d7-7883-4780-a1cd-5f2d00c65155, company:a1fd5777-7732-4e45-9036-11be529ec8bb, company:62cae47c-25ea-4a64-ba18-ec3eee464d96`
