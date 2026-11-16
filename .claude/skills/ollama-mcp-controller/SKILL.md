---
name: ollama-mcp-controller
description: Efficient local Ollama MCP integration for planning, bug checks, and small diff generation with minimal token consumption and security safeguards.
---

# Ollama MCP Controller Skill

## Purpose
Enables fast, low-token, private LLM interactions via local Ollama and local MCP server (`http://127.0.0.1:11434`).

## Security & Privacy Boundary
1. **Local Only**: Bind strictly to `127.0.0.1`. Never expose MCP ports externally.
2. **Strict Sanitization**: Never pass credentials, API keys, `.env` data, or protected directories (`requirement/Propose`).
3. **No Unsanctioned Shell Execution**: Never execute arbitrary shell code received from MCP responses without verification.

## Token Reduction Principles
1. **Snippet Over File**: Send only the target function or failing lines with 5 lines of surrounding context.
2. **Concise Instructions**: Request unified diffs or single-phrase answers.
3. **Single Task per Call**: Dispatch isolated tasks (e.g., "Find missing bracket in lines 40-60").
4. **Zero Fluff**: Do not include chat history or boilerplate markdown templates in MCP requests.

## VRAM Guard & Crash Prevention (4GB VRAM Protection)
Because the local GPU has **4GB VRAM (GTX 1050)**, Ollama default allocations (`num_ctx = 8192+`) will trigger CUDA Out-Of-Memory (OOM) crashes and kill the inference process.

### Safe Parameter Bounds
- **Strict Context Ceiling**: Always set `"num_ctx": 2048` (or max `3072` for `gemma2:2b`). Never allow unbounded or 8k+ context on 4GB VRAM.
- **Max Generation Tokens**: Cap `"num_predict": 512`.
- **Concurrency**: Set `"OLLAMA_NUM_PARALLEL=1"` to prevent concurrent VRAM fragmentation.

## Reusable Invocation Pattern (OOM-Safe)
```python
# Call local Ollama with strict VRAM-safe token boundaries
payload = {
    "model": "gemma2:2b",  # or local model
    "prompt": "Review diff only for syntax/security errors:\n" + target_diff,
    "stream": False,
    "options": {
        "num_ctx": 2048,      # Strict 2K token window prevents 4GB VRAM OOM crash
        "num_predict": 512,   # Cap generation size
        "temperature": 0.1
    }
}
```

