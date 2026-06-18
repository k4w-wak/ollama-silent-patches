#!/usr/bin/env python3
"""GPU Monitor — mergeret fra claw-code's StreamingOllamaClient.get_gpu_stats()
Giver Grok live GPU information."""
import subprocess
from typing import Dict, Any


def get_gpu_stats() -> Dict[str, Any]:
    """Get GPU memory usage and stats from nvidia-smi."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu,name',
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            parts = [p.strip() for p in result.stdout.strip().split(', ')]
            return {
                'memory_used_mb': int(parts[0]),
                'memory_total_mb': int(parts[1]),
                'gpu_util': int(parts[2]),
                'temperature': int(parts[3]),
                'name': parts[4] if len(parts) > 4 else 'unknown',
            }
    except:
        pass
    return {}


def print_gpu_status() -> str:
    """Formatted GPU status for display."""
    stats = get_gpu_stats()
    if not stats:
        return "[GPU] No NVIDIA GPU detected"
    
    util_color = "🟢" if stats['gpu_util'] > 50 else "🟡"
    temp_color = "🔴" if stats['temperature'] > 80 else "🟢"
    
    return (
        f"[GPU] {stats.get('name', 'NVIDIA')} "
        f"{util_color} {stats['gpu_util']}% util "
        f"{temp_color} {stats['temperature']}°C "
        f"{stats['memory_used_mb']}/{stats['memory_total_mb']} MiB"
    )
