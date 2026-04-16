import gc
import os
import torch
from pydantic import BaseModel
from typing import List, Literal, Union
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body
from sentence_transformers import SentenceTransformer

QUERY_INSTRUCT = os.getenv(
    "EMBED_QUERY_INSTRUCTION",
    "Given a catalog lookup query, retrieve the matching catalog item.",
)
QUERY_PROMPT = f"Instruct: {QUERY_INSTRUCT}\nQuery:"

class BatchRequest(BaseModel):
    texts: List[str]
    mode: Literal["doc", "query"] = "doc"

# Global variables
MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "Qwen/Qwen3-Embedding-0.6B")
model = None
device = None

class TextRequest(BaseModel):
    text: str
    mode: Literal["doc", "query"] = "doc"

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    dimension: int


def encode_kwargs(mode: Literal["doc", "query"]):
    if mode == "query" and "qwen" in MODEL_NAME.lower():
        return {"prompt": QUERY_PROMPT}
    return {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model optimized for Apple M4"""
    global model, device
    
    print("Initializing for Apple M4...")
    
    if torch.backends.mps.is_available():
        device = "mps"
        torch.backends.mps.enable_fallback = True
        print("Using Apple M4 GPU (MPS)")
    else:
        device = "cpu"
        print("MPS not available, using CPU")
    
    print(f"Loading model: {MODEL_NAME}")
    
    model = SentenceTransformer(
        MODEL_NAME,
        device=device,
        trust_remote_code=True
    )
    
    model.eval()
    
    print("Warming up model...")
    _ = model.encode("warmup", convert_to_numpy=True)
    
    print("Model ready! Optimized for Apple M4")
    yield
    print("Shutting down...")

app = FastAPI(title="M4-Optimized Embedding API", lifespan=lifespan)

@app.post("/embed", response_model=EmbeddingResponse)
async def get_embedding(request: TextRequest):
    """Generate embeddings optimized for M4"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Fast encoding with normalization
        embedding = model.encode(
            request.text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=1,
            **encode_kwargs(request.mode),
        )
        
        embedding_list = embedding.tolist()
        
        return EmbeddingResponse(
            embedding=embedding_list,
            dimension=len(embedding_list)
        )
    
    except Exception as e:
        print(f"request fail with error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/embed/batch")
async def get_embeddings_batch(payload: Union[List[str], BatchRequest] = Body(...)):
    """
    MPS-safe batch embedding:
      - server-side chunking
      - no torch.cat / huge buffer allocations
      - optional input truncation
      - empty_cache + gc on MPS
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if isinstance(payload, BatchRequest):
        texts = payload.texts
        mode = payload.mode
    else:
        texts = payload
        mode = "doc"

    if not texts:
        return {"embeddings": [], "count": 0, "dimension": 0}

    server_max_batch = int(os.getenv("EMBED_SERVER_MAX_BATCH", "16"))
    max_chars = int(os.getenv("EMBED_TEXT_MAX_CHARS", "2000"))

    # Truncate very long texts to avoid pathological allocations in tokenization
    safe_texts = [(t or "")[:max_chars] for t in texts]

    try:
        all_embeddings: List[List[float]] = []

        # Reduce peak memory with inference_mode/no_grad
        with torch.inference_mode():
            for i in range(0, len(safe_texts), server_max_batch):
                chunk = safe_texts[i : i + server_max_batch]
                vecs = model.encode(
                    chunk,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                    batch_size=min(8, len(chunk)),  # keep small on MPS
                    **encode_kwargs(mode),
                )
                all_embeddings.extend(vecs.tolist())

        dim = len(all_embeddings[0]) if all_embeddings else 0

        # Encourage memory release on MPS
        if torch.backends.mps.is_available():
            try:
                torch.mps.empty_cache()
            except Exception:
                pass
        gc.collect()

        return {"embeddings": all_embeddings, "count": len(all_embeddings), "dimension": dim}

    except RuntimeError as e:
        # Ensure we attempt to recover after OOM
        if torch.backends.mps.is_available():
            try:
                torch.mps.empty_cache()
            except Exception:
                pass
        gc.collect()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "status": "running",
        "device": str(device),
        "optimized_for": "Apple M4",
        "model": MODEL_NAME,
        "query_instruction": QUERY_INSTRUCT,
    }

@app.get("/health")
async def health():
    return {
        "ready": model is not None,
        "device": str(device),
        "model": MODEL_NAME,
        "query_instruction": QUERY_INSTRUCT,
        "mps_available": torch.backends.mps.is_available()
    }

if __name__ == "__main__":
    import uvicorn
    # Optimized uvicorn settings for M4
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=4000,
        workers=1,  # Single worker for MPS (GPU doesn't share well)
        log_level="info"
    )
