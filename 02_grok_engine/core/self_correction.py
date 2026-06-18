#!/usr/bin/env python3
"""Self-Correction Loop — mergeret fra claw-code's self_correction.py
Indbygget i Grok's agent loop for automatic retry med exponential backoff."""
import time
import json
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    TOOL_ERROR = "tool_error"
    PARSING_ERROR = "parsing_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT = "rate_limit"
    CONTEXT_OVERFLOW = "context_overflow"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    error_type: ErrorType
    message: str
    tool_name: str
    retry_count: int
    resolved: bool
    resolution: Optional[str] = None
    timestamp: float = 0.0


class SelfCorrectionLoop:
    """Self-correction loop med exponential backoff og fallback strategies.
    Mergeret fra claw-code SuperHeavyGrok."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.error_history: List[ErrorRecord] = []
        self.known_patterns = {
            "not found": ErrorType.TOOL_ERROR,
            "permission denied": ErrorType.TOOL_ERROR,
            "timeout": ErrorType.TIMEOUT_ERROR,
            "rate limit": ErrorType.RATE_LIMIT,
            "too many tokens": ErrorType.CONTEXT_OVERFLOW,
            "context length": ErrorType.CONTEXT_OVERFLOW,
            "connection": ErrorType.TIMEOUT_ERROR,
            "refused": ErrorType.TOOL_ERROR,
        }
        self.fallback_strategies = {
            ErrorType.TOOL_ERROR: self._fallback_tool_error,
            ErrorType.PARSING_ERROR: self._fallback_parsing_error,
            ErrorType.TIMEOUT_ERROR: self._fallback_timeout,
            ErrorType.RATE_LIMIT: self._fallback_rate_limit,
            ErrorType.CONTEXT_OVERFLOW: self._fallback_context_overflow,
            ErrorType.UNKNOWN: self._fallback_unknown,
        }

    def classify_error(self, error_message: str) -> ErrorType:
        el = error_message.lower()
        for pattern, etype in self.known_patterns.items():
            if pattern in el:
                return etype
        return ErrorType.UNKNOWN

    def execute_with_retry(self, tool_func: Callable, tool_name: str, input_data: str) -> Dict[str, Any]:
        last_error = None
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                if isinstance(input_data, str):
                    result = tool_func(input_data)
                elif isinstance(input_data, dict):
                    result = tool_func(**input_data)
                else:
                    result = tool_func(input_data)
                if isinstance(result, str) and ('[ERROR]' in result or '[FEJL]' in result):
                    raise Exception(result[:200])
                if retry_count > 0:
                    self.error_history.append(ErrorRecord(
                        error_type=ErrorType.UNKNOWN, message="resolved on retry",
                        tool_name=tool_name, retry_count=retry_count, resolved=True
                    ))
                return {'success': True, 'result': result, 'retries': retry_count}
            except Exception as e:
                last_error = str(e)
                etype = self.classify_error(last_error)
                fb = self.fallback_strategies.get(etype, self._fallback_unknown)(tool_func, tool_name, input_data, last_error, retry_count)
                if fb is not None:
                    return {'success': True, 'result': fb, 'retries': retry_count + 1}
                retry_count += 1
                if retry_count <= self.max_retries:
                    delay = min(self.base_delay * (2 ** (retry_count - 1)), self.max_delay)
                    time.sleep(delay)
        return {'success': False, 'error': last_error, 'retries': retry_count - 1}

    def _fallback_tool_error(self, tool_func, tool_name, input_data, error, retry_count):
        if isinstance(input_data, str):
            for alt in [input_data.strip(), input_data.replace('\n', ' '), input_data.split('\n')[0]]:
                if alt != input_data:
                    try:
                        r = tool_func(alt)
                        if '[ERROR]' not in str(r) and '[FEJL]' not in str(r):
                            return r
                    except:
                        pass
        return None

    def _fallback_parsing_error(self, tool_func, tool_name, input_data, error, retry_count):
        try:
            if isinstance(input_data, str):
                return tool_func(' '.join(input_data.split()[:50]))
        except:
            pass
        return None

    def _fallback_timeout(self, tool_func, tool_name, input_data, error, retry_count):
        return None  # Just retry with backoff

    def _fallback_rate_limit(self, tool_func, tool_name, input_data, error, retry_count):
        time.sleep(5)
        try:
            if isinstance(input_data, str):
                return tool_func(input_data)
            elif isinstance(input_data, dict):
                return tool_func(**input_data)
        except:
            pass
        return None

    def _fallback_context_overflow(self, tool_func, tool_name, input_data, error, retry_count):
        if isinstance(input_data, str):
            try:
                return tool_func(input_data[:1000] + "...")
            except:
                pass
        return None

    def _fallback_unknown(self, tool_func, tool_name, input_data, error, retry_count):
        return None
