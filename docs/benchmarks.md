# Benchmark Results

**Recorded:** 2026-10-18
**Machines:** RTX-2050-laptop, CPU-only-16GB-laptop
**Fixture:** D1_clean_lease.pdf (8 answerable prompts)
**Ollama env:** OLLAMA_HOST=127.0.0.1, OLLAMA_NUM_PARALLEL=1, OLLAMA_MAX_LOADED_MODELS=1

## Results Table

| Model | Machine | Size (GB) | Peak RAM (GB) | Peak VRAM (GB) | TTFT (s) | Tok/s | JSON Valid % | Quote Acc % |
|-------|---------|-----------|---------------|----------------|----------|-------|--------------|-------------|
| gemma3n:e2b | RTX-2050-laptop | 7.8 | X.X | X.X | X.X | X.X | XX% | XX% |
| gemma3n:e2b | CPU-only-16GB | 7.8 | X.X | 0 | X.X | X.X | XX% | XX% |
| gemma4:e2b | RTX-2050-laptop | X.X | X.X | X.X | X.X | X.X | XX% | XX% |
| gemma4:e2b | CPU-only-16GB | X.X | X.X | 0 | X.X | X.X | XX% | XX% |
| gemma4:e2b-it-qat | RTX-2050-laptop | 4.3 | X.X | X.X | X.X | X.X | XX% | XX% |
| gemma4:e2b-it-qat | CPU-only-16GB | 4.3 | X.X | 0 | X.X | X.X | XX% | XX% |

## Selection Record

**Chosen model:** `___` (date, who, numbers: CPU-only loads, <2min, 100% JSON valid, highest quote accuracy)
**Recorded in:** `src/config.py` `MODEL_NAME` and `docs/PROJECT_MASTER.md` §7.3

## Request Configuration (for reproducibility)

```json
{
  "stream": true,
  "format": "json",
  "think": false,
  "keep_alive": "5m",
  "options": { "temperature": 0, "num_ctx": 8192 }
}
```

**Note on JSON validity granularity:** With N=8 prompts, ">90%" requires 8/8 = 100% (7/8 = 87.5% fails). This is recorded explicitly per RESEARCH.md Pattern 2 granularity caveat.