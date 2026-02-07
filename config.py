"""
GRC Toolkit Configuration
==========================
Location: grc_toolkit/config.py
"""

import os

# ──────────────────────────────────────────────
# API Configuration — ANTHROPIC CLAUDE
# ──────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "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")

# Model options:
#   "claude-sonnet-4-20250514"   — Best balance of speed/quality/cost (recommended)
#   "claude-3-5-haiku-20241022" — Fastest, cheapest
#   "claude-3-opus-20240229"    — Most capable, slowest, most expensive
MODEL = "claude-sonnet-4-20250514"

# Max tokens for responses
MAX_TOKENS = 4096

# ──────────────────────────────────────────────
# Supported Frameworks
# ──────────────────────────────────────────────
SUPPORTED_FRAMEWORKS = [
    "NIST CSF 2.0",
    "ISO 27001:2022",
    "SOC 2 Type II",
    "HIPAA",
    "PCI DSS 4.0",
    "CMMC 2.0",
    "NIST 800-53 Rev 5",
    "CIS Controls v8",
    "GDPR",
]

# ──────────────────────────────────────────────
# Company defaults (overridden per engagement)
# ──────────────────────────────────────────────
DEFAULT_COMPANY = {
    "name": "",
    "industry": "",
    "size": "",
    "description": "",
}

# ──────────────────────────────────────────────
# Output paths
# ──────────────────────────────────────────────
OUTPUT_DIR = "outputs"
GAP_ASSESSMENT_DIR = f"{OUTPUT_DIR}/gap_assessments"
POLICY_DIR = f"{OUTPUT_DIR}/policies"
PROCEDURE_DIR = f"{OUTPUT_DIR}/procedures"
REPORT_DIR = f"{OUTPUT_DIR}/reports"
