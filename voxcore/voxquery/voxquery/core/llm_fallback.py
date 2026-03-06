"""
LLM Fallback System - Automatic model switching on rate limits
Ensures reliability: Primary model (70B) → Fallback model (8B) if rate limited
"""

import os
import logging
from groq import Groq
from typing import Optional

logger = logging.getLogger(__name__)

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_sql_with_fallback(
    messages: list,
    temperature: float = 0.1,
    max_tokens: int = 1024,
) -> str:
    """
    Generate SQL with automatic fallback to smaller model on rate limit.
    
    Flow:
    1. Try primary model (llama-3.3-70b-versatile)
    2. If rate limited (429), fall back to llama-3.1-8b-instant
    3. If both fail, raise exception with clear error
    
    Args:
        messages: Chat messages for LLM
        temperature: Model temperature (0.1 = deterministic)
        max_tokens: Max tokens in response
        
    Returns:
        Generated SQL string
        
    Raises:
        Exception: If both models fail
    """
    
    # Try primary model first
    logger.info(f"[LLM] Attempting primary model: {PRIMARY_MODEL}")
    try:
        response = groq_client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logger.info("[LLM] ✅ Primary model succeeded")
        return response.choices[0].message.content
        
    except Exception as primary_error:
        # Check if it's a rate limit error
        error_str = str(primary_error)
        
        if "429" in error_str or "rate_limit" in error_str.lower():
            logger.warning(f"[LLM] 🔄 Rate limited on {PRIMARY_MODEL}: {error_str[:100]}")
            logger.info(f"[LLM] 🔄 Falling back to: {FALLBACK_MODEL}")
            
            # Try fallback model
            try:
                response = groq_client.chat.completions.create(
                    model=FALLBACK_MODEL,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                logger.info(f"[LLM] ✅ Fallback successful: {FALLBACK_MODEL}")
                return response.choices[0].message.content
                
            except Exception as fallback_error:
                logger.error(
                    f"[LLM] ❌ Both models failed. "
                    f"Primary: {str(primary_error)[:100]}, "
                    f"Fallback: {str(fallback_error)[:100]}"
                )
                raise Exception(
                    f"LLM generation failed on both models. "
                    f"Primary error: {primary_error}, "
                    f"Fallback error: {fallback_error}"
                )
        else:
            # Not a rate limit error, re-raise immediately
            logger.error(f"[LLM] ❌ Primary model failed (non-rate-limit): {error_str[:100]}")
            raise primary_error
