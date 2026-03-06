#!/usr/bin/env python
"""Direct test of Groq API to verify it's working correctly"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("ERROR: GROQ_API_KEY not set in .env")
    exit(1)

print(f"✓ GROQ_API_KEY loaded: {groq_api_key[:20]}...")

# Initialize Groq with llama-3.3-70b-versatile (current stable model)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=groq_api_key,
    temperature=0.0,
    max_tokens=1024,
)

print("✓ Groq client initialized with llama-3.3-70b-versatile\n")

# Test 1: Simple SQL generation
print("="*80)
print("TEST 1: Generate SQL for 'Show top 5 items by price'")
print("="*80)

prompt1 = """You are a SQL expert. Generate SQL ONLY.

Schema: menu(menu_id int, truck_brand_name text, sale_price_usd decimal)

Question: Show top 5 items by price

Response (SQL ONLY):"""

response1 = llm.invoke(prompt1)
print(f"Response:\n{response1.content}\n")

# Test 2: Different question
print("="*80)
print("TEST 2: Generate SQL for 'Count unique truck brands'")
print("="*80)

prompt2 = """You are a SQL expert. Generate SQL ONLY.

Schema: menu(menu_id int, truck_brand_name text, sale_price_usd decimal)

Question: Count unique truck brands

Response (SQL ONLY):"""

response2 = llm.invoke(prompt2)
print(f"Response:\n{response2.content}\n")

# Test 3: Another different question
print("="*80)
print("TEST 3: Generate SQL for 'Average sale price by truck brand'")
print("="*80)

prompt3 = """You are a SQL expert. Generate SQL ONLY.

Schema: menu(menu_id int, truck_brand_name text, sale_price_usd decimal)

Question: Average sale price by truck brand

Response (SQL ONLY):"""

response3 = llm.invoke(prompt3)
print(f"Response:\n{response3.content}\n")

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Test 1 SQL: {response1.content.strip()}")
print(f"Test 2 SQL: {response2.content.strip()}")
print(f"Test 3 SQL: {response3.content.strip()}")

if response1.content.strip() == response2.content.strip() == response3.content.strip():
    print("\n❌ ERROR: All responses are identical! Groq is returning the same SQL.")
else:
    print("\n✓ SUCCESS: Responses are different. Groq is working correctly.")
