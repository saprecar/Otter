---
name: free-llm-router
description: Configures and manages free-tier LLM proxy routers (OmniRoute, LiteLLM) during Development and Testing, enforcing strict rate limits and privacy boundaries.
---

# Free LLM Router Skill

## Scope & Boundary
1. **Development & Testing Only**: Free-tier proxy routing (Groq, Gemini Free, OpenRouter, Cerebras) is strictly restricted to `Dev/`, local testing, and MCP planning tasks. It is **PROHIBITED** in production or official stable releases.
2. **Never Send Sensitive Data**: Never transmit confidential business logic, private user info, passwords, or API keys over public free tiers (especially Google AI Studio free tier which permits model training).
3. **Local Failover**: When free quotas or HTTP 429 rate limits are reached, failover immediately to local Ollama (`gemma2:2b`) with 2048 token context bounds.

---

## Free-Tier Provider Limits & Constraints

| Provider | Model Family | Daily Limit | RPM Cap | Max Context / Output | Privacy Constraint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GroqCloud** | `qwen2.5-coder-32b`, `llama-3.3-70b` | ~1,000 requests/day | 25 RPM | 2048 output tokens | High speed; zero data training |
| **Google AI Studio** | `gemini-2.0-flash`, `gemini-1.5-flash` | 1,500 requests/day | 15 RPM | 4096 context tokens | Free tier data used for training; sanitize all PII |
| **OpenRouter (`:free`)** | `deepseek/deepseek-r1:free`, `qwen:free` | 50-200 requests/day | 20 RPM | 2048 output tokens | Auto-failover on HTTP 429 |
| **Local Ollama** | `gemma2:2b` | Unlimited | Local | 2048 context (4GB GPU safe) | 100% offline & private fallback |

---

## MCP Proxy Setup & Routing Pattern

Run local router binding to localhost:
```bash
# Using LiteLLM proxy (OpenAI compatible on 127.0.0.1:8000):
litellm --config dev_router_config.yaml --port 8000
```

### Failover Order Configuration
```yaml
# [AI-BLOCK: Router Failover Chain]
model_list:
  - model_name: coder-primary
    litellm_params:
      model: groq/qwen-2.5-coder-32b
      api_key: os.environ/GROQ_API_KEY
  - model_name: coder-primary
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY
  - model_name: coder-primary
    litellm_params:
      model: ollama/gemma2:2b
      api_base: http://127.0.0.1:11434
```

### Rate-Limit Circuit Breaker
- When receiving HTTP 429 (Too Many Requests), do not retry in an aggressive loop.
- Wait 5 seconds, switch to the next tier in the failover chain, or fall back to local Ollama.

