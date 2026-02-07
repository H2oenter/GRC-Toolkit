#!/usr/bin/env python3
"""
Quick Start — Test that Anthropic API works with the toolkit.
Location: grc_toolkit/quickstart.py

Run with: python quickstart.py
"""

import os

# Create directories
for d in ["outputs/gap_assessments", "outputs/policies",
          "outputs/procedures", "outputs/reports", "frameworks"]:
    os.makedirs(d, exist_ok=True)

import config

# Pre-flight check
print("=" * 50)
print("  GRC Toolkit — Quick Start Test")
print("=" * 50)

print(f"\n  Model: {config.MODEL}")
key_preview = config.ANTHROPIC_API_KEY[:12] + "..." if len(config.ANTHROPIC_API_KEY) > 12 else "NOT SET"
print(f"  API Key: {key_preview}")

if config.ANTHROPIC_API_KEY == "your-anthropic-api-key-here":
    print("\n  ❌ API key not configured!")
    print("  Set it: export ANTHROPIC_API_KEY='sk-ant-...'")
    print("  Or edit config.py")
    exit(1)

# Test 1: Basic AI call
print("\n  Test 1: Basic AI connection...")
from utils.ai_client import chat, structured_output

try:
    response = chat(
        "You are a helpful assistant.",
        "Say 'GRC Toolkit is working!' and nothing else.",
        temperature=0.0,
        max_tokens=50,
    )
    print(f"  ✅ AI Response: {response.strip()}")
except Exception as e:
    print(f"  ❌ AI connection failed: {e}")
    exit(1)

# Test 2: Structured output
print("\n  Test 2: Structured JSON output...")
try:
    result = structured_output(
        "You are a GRC expert.",
        "List 3 common security frameworks. Return as JSON array of objects with 'name' and 'description' keys.",
        max_tokens=500,
    )
    print(f"  ✅ Got structured output: {type(result).__name__}")
    if isinstance(result, list):
        for item in result[:3]:
            print(f"     - {item.get('name', 'N/A')}")
    elif isinstance(result, dict):
        items = result.get("frameworks", list(result.values())[0] if result else [])
        if isinstance(items, list):
            for item in items[:3]:
                if isinstance(item, dict):
                    print(f"     - {item.get('name', str(item))}")
except Exception as e:
    print(f"  ❌ Structured output failed: {e}")

# Test 3: Generate a short policy
print("\n  Test 3: Policy generation...")
from engines.policy_generator import PolicyGenerator

company = {
    "name": "TechCorp Inc",
    "industry": "Financial Technology",
    "size": "350 employees",
    "description": "Cloud-based payment processing platform",
}

try:
    gen = PolicyGenerator(company)
    policy = gen.generate_policy(
        "Password Policy",
        framework="SOC 2 Type II",
        additional_context="We use Okta for SSO.",
    )
    print(f"  ✅ Generated policy: {len(policy):,} characters")
    print(f"\n  Preview (first 500 chars):")
    print(f"  {'─'*45}")
    print(f"  {policy[:500]}")
    print(f"  {'─'*45}")

    # Save it
    path = gen.save_document(policy, "policy", "Password_Policy_TEST")
except Exception as e:
    print(f"  ❌ Policy generation failed: {e}")

print("\n" + "=" * 50)
print("  ✅ All tests passed! Toolkit is ready.")
print("=" * 50)
print("\n  Next steps:")
print("    python main.py          — CLI interface")
print("    streamlit run web_app.py — Web UI")
print()