# YouTube RAG — Project Plan

Goal: a **highly configurable Streamlit app** for chatting with YouTube videos using RAG, not just a plain site.
Approach: build **one piece at a time** and understand each concept before moving on. Prefer free providers.

Legend: `[x]` done · `[~]` partly done · `[ ]` not started

---

## Phase 0 — Basic pipeline (learning stage)

- [x] Fetch a transcript with `youtube-transcript-api` (`system/indexing.py`)
- [x] Split text into chunks: `RecursiveCharacterTextSplitter`, 1000 chars / 200 overlap (`system/splitters.py`)
- [x] Embeddings with free HF `all-MiniLM-L6-v2`, stored in FAISS (`system/embedding.py`)
- [x] `.env` + `load_dotenv()` for `HF_TOKEN` / `GROQ_API_KEY`
- [x] Retriever wrapper `retrieve(vector_store, search_type, search_kwargs)` (`system/retriever.py`)
- [x] Augmentation builds the prompt only (`system/augmentation.py`)
- [x] Generation with Groq `openai/gpt-oss-20b`, falling back to `qwen/qwen3.8-27b` when busy or rate-limited (`system/generation.py`). Qwen's free tier allows 1000 output tokens/min, so it needs `max_tokens` below that. Errors are raised as `GenerationError`.
- [x] Pipeline ran end to end
- [x] Concepts covered: embeddings, similarity search, `k`, FAISS distance scores (lower = closer), score threshold
- [x] Refactored into two callable functions the UI uses:
  - `build_index(video_id, language)` → vector store (`system/indexing.py`)
  - `answer_question(vector_store, question)` → answer (`system/answering.py`)
- [x] Transcript functions moved to `system/transcript.py`

## Phase 1 — Robust YouTube input (pure Python, no UI)

- [x] Accept any URL format and extract the ID: `watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/live/`, raw ID (`extract_video_id`)
- [x] Language fallback: requested language (manual → auto) → translation → original language (`fetch_transcript`, `fetch_translated_or_original`). YouTube often blocks translated captions, so it falls back to the original language.
- [x] `list_language(video_id)` returns the available languages for a UI dropdown, so the user only picks codes that exist (also solves `en` vs `en-US`)
- [x] Clear error messages: `TranscriptError` with a `code`, mapped from library exceptions in `system/transcripterror_handler.py`. Errors are raised, not returned. Covers:
  - [x] Transcripts disabled
  - [x] No transcript found / language missing (falls back instead of crashing)
  - [x] Video unavailable / private / invalid ID
  - [x] YouTube IP block / rate limit, network errors, age-restricted, empty captions
- [ ] **Decision:** keep timestamps in the chunks (currently joined into one string, so they're lost). Needed for "discussed at 12:34" citations in Phase 5. Changing this later means redoing indexing.

## Phase 2 — Config foundation

- [ ] One settings object: provider, model, API keys, embedding model, vector store, `k`, search type, chunk size/overlap, etc.
- [ ] Every pipeline function reads from that object instead of hardcoded values

## Phase 3 — Basic Streamlit UI

- [x] Video URL input → language dropdown (`st.cache_data`) → "Load video" button
- [x] Chat interface (`st.chat_input` / `st.chat_message`) with history in `st.session_state`, reset per video, plus a "Start fresh" button
- [x] `@st.cache_resource(max_entries=5)` for the per-video vector store; embedding model loaded once (`lru_cache` in `system/embedding.py`)
- [x] YouTube and Groq errors shown with `st.error` instead of crashing
- [ ] Profile/settings icon in the corner (`st.popover` or `st.dialog`) that edits the config
- [ ] API keys kept in `st.session_state` only: never written to disk, never logged

## Phase 4 — Pluggable providers (registry pattern)

- [ ] LLMs: Groq (current), OpenAI, Gemini, Ollama
- [ ] Embeddings: Hugging Face (current), OpenAI
- [ ] Vector stores: FAISS (current), Pinecone shown as "coming soon"
- [ ] A small registry, so adding a provider means one new file and no other changes

## Phase 5 — Advanced retrieval & augmentation

- Retrieval
  - [ ] MMR
  - [ ] Score threshold (`similarity_score_threshold`)
  - [ ] Multi-query
  - [ ] Reranking
  - [ ] Contextual compression
- Augmentation & generation
  - [ ] Selectable prompt templates
  - [ ] Answers with citations (video timestamps)
  - [ ] Guardrails

## Phase 6 — Evaluation

- [ ] Ragas
- [ ] LangSmith

---

## Production concerns (later, for reference)

Ingestion at scale, persistent vector DB with metadata filters, hybrid search, caching / latency / cost, monitoring, prompt-injection protection.

## Notes

- Run the pipeline: `python -m system.indexing` from the project root
- Run the app: `streamlit run app.py`
- Groq models available to the key: `from groq import Groq; print([m.id for m in Groq().models.list().data])`
- Venv was fixed after the drive moved from `/run/media/vijay/D0D804DDD804C3A6` to `/mnt/data` (fstab now mounts it there on every boot)
