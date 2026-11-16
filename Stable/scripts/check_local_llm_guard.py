#!/usr/bin/env python3
# [AI-BLOCK: Multi-System Hardware Profiler & VRAM Adaptive Token Guard]
"""
Auto-detects active machine hardware and dynamically calculates safe token context windows,
concurrency limits, and recommended local model sizes.

Supported Machine Profiles:
1. Mobile / Laptop: GTX 1050 (4GB VRAM, 16GB DDR4) -> Safe num_ctx: 2048, models: 2B - 3B
2. Workstation / Rig: RTX 5070 Ti (16GB VRAM, 32GB DDR5-6000, i7-14700F) -> Safe num_ctx: 16384-32768, models: 14B - 32B / MoE
"""

import subprocess
import json
import sys

# [AI-BLOCK: Query Active GPU Specs via nvidia-smi]
def detect_gpu():
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=True
        )
        line = res.stdout.strip().splitlines()[0]
        parts = [x.strip() for x in line.split(",")]
        name = parts[0]
        total_mb, free_mb, used_mb = int(parts[1]), int(parts[2]), int(parts[3])
        return {
            "has_gpu": True,
            "gpu_name": name,
            "total_vram_mb": total_mb,
            "free_vram_mb": free_mb,
            "used_vram_mb": used_mb
        }
    except Exception:
        return {
            "has_gpu": False,
            "gpu_name": "CPU-Only / Unknown",
            "total_vram_mb": 0,
            "free_vram_mb": 0,
            "used_vram_mb": 0
        }

# [AI-BLOCK: Dynamic Hardware Tier Profiling]
def profile_hardware():
    gpu = detect_gpu()
    
    if not gpu["has_gpu"]:
        return {
            "tier": "CPU_FALLBACK",
            "device": "CPU / System RAM",
            "vram_gb": 0,
            "recommended_ctx": 2048,
            "max_predict": 512,
            "recommended_models": ["gemma2:2b", "qwen2.5-coder:1.5b"],
            "colibri_support": True,
            "notes": "No NVIDIA GPU active. Keep context small to avoid high CPU latency."
        }
    
    total_vram = gpu["total_vram_mb"]
    gpu_name = gpu["gpu_name"]
    free_vram = gpu["free_vram_mb"]
    
    # Tier 1: High-Performance Rig (RTX 5070 Ti or 12GB+ GPU)
    if total_vram >= 12000:
        return {
            "tier": "WORKSTATION_PRO",
            "device": f"{gpu_name} ({round(total_vram/1024, 1)} GB VRAM)",
            "vram_gb": round(total_vram/1024, 1),
            "free_vram_mb": free_vram,
            "recommended_ctx": 16384,
            "max_predict": 2048,
            "recommended_models": [
                "qwen2.5-coder:14b",
                "qwen2.5-coder:32b (4-bit)",
                "deepseek-r1:14b",
                "mistral-nemo:12b"
            ],
            "colibri_support": True,
            "notes": "Full GPU acceleration. Safe for heavy multi-file reasoning and large context up to 32k."
        }
    
    # Tier 2: Mid-Range GPU (6GB - 10GB VRAM)
    elif total_vram >= 6000:
        return {
            "tier": "MID_RANGE",
            "device": f"{gpu_name} ({round(total_vram/1024, 1)} GB VRAM)",
            "vram_gb": round(total_vram/1024, 1),
            "free_vram_mb": free_vram,
            "recommended_ctx": 4096,
            "max_predict": 1024,
            "recommended_models": ["qwen2.5-coder:7b", "llama3.1:8b"],
            "colibri_support": True,
            "notes": "Moderate GPU capacity. Cap context at 4096 tokens to avoid swapping."
        }
    
    # Tier 3: Constrained / Laptop GPU (GTX 1050 4GB or less)
    else:
        return {
            "tier": "LAPTOP_CONSTRAINED",
            "device": f"{gpu_name} ({round(total_vram/1024, 1)} GB VRAM)",
            "vram_gb": round(total_vram/1024, 1),
            "free_vram_mb": free_vram,
            "recommended_ctx": 2048,
            "max_predict": 512,
            "recommended_models": ["gemma2:2b", "qwen2.5-coder:1.5b", "qwen2.5-coder:3b"],
            "colibri_support": True,
            "notes": "Strict 2048 context ceiling required to prevent CUDA Out-Of-Memory (OOM) crashes."
        }

# [AI-BLOCK: CLI Output Formatter]
def main():
    profile = profile_hardware()
    print("==================================================")
    print("      Adaptive Local Hardware & LLM Profiler      ")
    print("==================================================")
    print(f"Active Hardware Tier : {profile['tier']}")
    print(f"Detected Device      : {profile['device']}")
    print(f"Recommended Context  : {profile['recommended_ctx']} tokens (num_ctx)")
    print(f"Max Predict Tokens   : {profile['max_predict']} tokens (num_predict)")
    print(f"Recommended Models   : {', '.join(profile['recommended_models'])}")
    print(f"Colibri MoE Engine   : {'Supported' if profile['colibri_support'] else 'Disabled'}")
    print(f"Operational Notes    : {profile['notes']}")
    print("==================================================")

if __name__ == "__main__":
    main()
