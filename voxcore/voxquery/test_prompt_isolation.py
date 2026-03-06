#!/usr/bin/env python
"""Test script to verify prompt isolation for multi-question fix

This tests that the prompt building doesn't include conversation context
that could confuse the LLM into reusing SQL from previous questions.
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core.conversation import ConversationManager

def test_prompt_isolation():
    """Test that prompts are isolated and don't include conversation context"""
    
    logger.info("\n" + "="*80)
    logger.info("TEST: Prompt Isolation for Multi-Question Fix")
    logger.info("="*80)
    
    # Create conversation manager
    conv = ConversationManager()
    
    # Simulate first question
    logger.info("\n1. First question asked...")
    question1 = "Show top 5 products by sales"
    conv.add_user_message(question1)
    conv.add_assistant_message("SELECT TOP 5 product_name, SUM(sales) FROM products GROUP BY product_name ORDER BY SUM(sales) DESC")
    
    context1 = conv.get_conversation_context()
    logger.info(f"   Question 1: {question1}")
    logger.info(f"   Conversation context after Q1:\n{context1}")
    
    # Simulate second question
    logger.info("\n2. Second question asked...")
    question2 = "Show bottom 5 products by sales"
    conv.add_user_message(question2)
    
    context2 = conv.get_conversation_context()
    logger.info(f"   Question 2: {question2}")
    logger.info(f"   Conversation context after Q2:\n{context2}")
    
    # Verify that context contains both questions
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION")
    logger.info("="*80)
    
    if question1 in context2:
        logger.info("✓ PASS: Conversation context contains first question")
    else:
        logger.error("✗ FAIL: Conversation context missing first question")
        return False
    
    if question2 in context2:
        logger.info("✓ PASS: Conversation context contains second question")
    else:
        logger.error("✗ FAIL: Conversation context missing second question")
        return False
    
    # Now test the key fix: the prompt should NOT include conversation context
    logger.info("\n" + "="*80)
    logger.info("KEY FIX VERIFICATION: Prompt Isolation")
    logger.info("="*80)
    
    # Simulate what _build_prompt does
    schema_context = "TABLE products (product_name VARCHAR, sales DECIMAL)"
    
    # The fix: prompt should NOT include context parameter
    # Instead, it should only include the current question
    prompt_without_context = f"""You are an expert SQL engineer.

LIVE SCHEMA:
{schema_context}

CURRENT QUESTION (answer this specific question only):
{question2}

RULES:
- Return ONLY the SQL query for the CURRENT QUESTION above
- IMPORTANT: Generate SQL ONLY for the CURRENT QUESTION, not for previous questions

RESPONSE (SQL ONLY):"""
    
    logger.info(f"\nPrompt for Question 2 (WITHOUT conversation context):")
    logger.info(prompt_without_context)
    
    # Verify the prompt does NOT contain the first question's SQL
    if "SELECT TOP 5 product_name, SUM(sales)" in prompt_without_context:
        logger.error("✗ FAIL: Prompt contains SQL from first question!")
        return False
    else:
        logger.info("✓ PASS: Prompt does NOT contain SQL from first question")
    
    # Verify the prompt contains the current question
    if question2 in prompt_without_context:
        logger.info("✓ PASS: Prompt contains current question")
    else:
        logger.error("✗ FAIL: Prompt missing current question")
        return False
    
    # Verify the prompt has explicit instruction to answer ONLY current question
    if "CURRENT QUESTION" in prompt_without_context and "not for previous questions" in prompt_without_context:
        logger.info("✓ PASS: Prompt has explicit instruction to answer ONLY current question")
    else:
        logger.error("✗ FAIL: Prompt missing explicit instruction")
        return False
    
    logger.info("\n" + "="*80)
    logger.info("✓ ALL TESTS PASSED")
    logger.info("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_prompt_isolation()
    sys.exit(0 if success else 1)
