---
name: ai-ml
description: "AI/ML: RAG pipeline, embeddings, reranking, vector search (Qdrant), graph (FalkorDB), LightRAG, chonkie chunking, DeepEval + Ragas evaluation, PyTorch training, MLflow tracking, Modal workers."
---

# AI/ML Engineering

## Khi nao dung

- RAG pipeline: Triple Fusion Retrieval, data ingestion, semantic cache
- Embeddings: Gemini Embedding 2 (multimodal), Qwen3 Embedding (text-only)
- Reranking: Qwen3 Reranker (text), Qwen3-VL Reranker (visual), dynamic routing
- Vector search: Qdrant collections, filters, MRL dimensionality
- Graph: FalkorDB, LightRAG dual-level queries (local/global)
- Chunking: chonkie (semantic + layout-aware), parent-child
- OCR: DeepSeek-OCR-2 (PDF/image extraction)
- ASR/TTS: Qwen3-ASR, Qwen3-TTS (Modal selfhost)
- Evaluation: DeepEval (CI-ready) + Ragas (RAG-specific metrics)
- PyTorch training, fine-tuning, HuggingFace, experiment tracking
- MLflow tracing (AI pipelines) va experiment tracking
- Modal.com GPU-serverless workers

## Model Selection

| Loai | Model | Ghi chu |
|------|-------|---------|
| LLM | Gemini 3 Pro / Flash | Primary |
| LLM Fallback | Grok 4.1 Fast Reasoning / Non-Reasoning | NSFW content |
| Multimodal Embedding | Gemini Embedding 2 | Primary (3072D, MRL, text/image/video/audio/PDF) |
| Text Embedding | Qwen3-Embedding-0.6B / 8B | Light / Heavy (text-only, Modal selfhost) |
| Text Reranker | Qwen3-Reranker-0.6B / 8B | Light / Heavy (Modal selfhost) |
| VL Reranker | Qwen3-VL-Reranker-2B / 8B | Light / Heavy (Modal selfhost) |
| OCR | DeepSeek-OCR-2 | Document extraction (3.34B MoE, Modal selfhost) |
| ASR | Qwen3-ASR-0.6B / 1.7B | Audio transcription (Modal selfhost) |
| TTS | Qwen3-TTS-12Hz-0.6B / 1.7B-CustomVoice | Speech synthesis (Modal selfhost) |
| Image | Gemini 3 Pro Image (Nano Banana Pro) | Primary |
| Image Fallback | Grok Imagine Image Pro | NSFW content |
| RAG Evaluation | DeepEval + Ragas | DeepEval primary (CI-ready), Ragas for RAG-specific metrics |
| Chunking | chonkie | Semantic + layout-aware chunking, Qdrant integration |

## References (doc on demand)

- `references/rag-pipeline.md` -- Triple Fusion RAG, 3-Fusion ingestion, chunking, retrieval, reranking, CRAG, evaluation, guardrails, semantic cache
- `references/dl-training.md` -- PyTorch training workflow, HuggingFace, MLflow experiment tracking, optimization techniques

Doc reference file tuong ung TRUOC KHI bat dau lam viec tren topic do.

## Spec / Plan / Training Roadmap

**BAT BUOC**: Khi user yeu cau viet spec/plan/roadmap cho bat ky AI/ML task nao (training pipeline, eval suite, RAG redesign, model finetune, data pipeline), invoke `Skill` tool voi `superpowers:writing-plans` (hoac `superpowers:brainstorming` cho ideation stage, `superpowers:executing-plans` cho execution) TRUOC KHI viet noi dung. KHONG freehand. Skill enforce verify-before-claim, test-first, bite-sized tasks, review checkpoint. Xem global rule `~/.claude/CLAUDE.md` section 1 va memory `feedback_spec_plan_superpower.md`.

**FEEDBACK → SPEC + PLAN**: Khi user dua feedback thay doi scope/requirements/decisions, PHAI cap nhat spec + plan document TRUOC, KHONG chi ghi memory. Memory la ghi chu bo sung, spec + plan la source of truth. Thu tu: feedback → (1) update spec/plan → (2) ghi memory → (3) implement.

**Public release readiness**: Moi training run / model checkpoint / eval report viet voi gia dinh se push len HuggingFace Hub public. Bat buoc:
- Model card theo HF template (task, intended use, training data, eval, limitations, license, citation)
- Dataset card neu release data (source attribution, license, stats, language distribution, PII scrubbing proof)
- Eval tren public benchmarks reproducible (BEIR, MMEB, MIRACL, MMDocIR, ViDoRe, AudioCaps, CMTEB)
- License: Apache-2.0 cho code + weights, CC-BY-4.0 hoac ODC-BY cho datasets
- KHONG hardcode AWS account ID, IAM user prefix, skret SSM full path, Modal workspace name, internal MLflow URL, personal email vao artifact

## Quy tac chung

- **DataFrames**: `polars` only (KHONG pandas).
- **LLM calls**: Direct SDK (OpenAI, Cohere, google-genai) voi per-app Bearer token tu skret SSM (`/<app>/prod/*` namespace). KHONG proxy middleware.
- **Comments/docstrings**: Tieng Viet.
- **Test Coverage**: >= 95%.
- **Reproducibility**: Set explicit random seeds, log hyperparameters + git commit hash vao MLflow.
- **Output format**: safetensors cho model checkpoints, JSONL cho datasets.
- **Experiment tracking**: MLflow tren infra-vnic (noi bo). Eval results copy sang HF model card khi release public.
