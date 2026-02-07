"""
Centralized AI Client — Anthropic Claude
==========================================
Location: grc_toolkit/utils/ai_client.py

All LLM calls go through this module.
Switching from OpenAI to Anthropic only requires changing THIS file.

Anthropic API differences from OpenAI:
- Uses "system" as a separate parameter (not in messages array)
- Messages array only contains "user" and "assistant" roles
- Response structure: response.content[0].text
- No "max_tokens" default — MUST be specified
"""

import anthropic
import json
import time
import config

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.3,
         model: str = None, max_tokens: int = None) -> str:
    """
    Send a single-turn chat completion request to Claude.
    
    Args:
        system_prompt: System instructions (Claude's role/behavior)
        user_prompt: The user's question/request
        temperature: 0.0-1.0 (lower = more consistent, good for GRC)
        model: Override default model
        max_tokens: Override default max tokens
    
    Returns:
        str: Claude's response text
    """
    try:
        response = client.messages.create(
            model=model or config.MODEL,
            max_tokens=max_tokens or config.MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
        )
        return response.content[0].text
    except anthropic.RateLimitError:
        print("[WARN] Rate limited. Waiting 30 seconds...")
        time.sleep(30)
        return chat(system_prompt, user_prompt, temperature, model, max_tokens)
    except anthropic.APIError as e:
        print(f"[ERROR] Anthropic API error: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] AI call failed: {e}")
        raise


def chat_with_context(system_prompt: str, messages: list,
                      temperature: float = 0.3,
                      max_tokens: int = None) -> str:
    """
    Multi-turn conversation — useful for iterative refinement.
    
    Args:
        system_prompt: System instructions
        messages: List of {"role": "user"/"assistant", "content": "..."}
                  NOTE: Anthropic requires alternating user/assistant messages
                  and the first message must be from "user"
        temperature: 0.0-1.0
    
    Returns:
        str: Claude's response text
    """
    # Validate message format for Anthropic
    validated_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        # Anthropic only accepts "user" and "assistant" in messages
        if role == "system":
            # Append system content to the system_prompt instead
            system_prompt += f"\n\n{msg['content']}"
            continue
        validated_messages.append({
            "role": role,
            "content": msg["content"]
        })
    
    # Ensure first message is from user (Anthropic requirement)
    if validated_messages and validated_messages[0]["role"] != "user":
        validated_messages.insert(0, {
            "role": "user",
            "content": "Please continue."
        })

    try:
        response = client.messages.create(
            model=config.MODEL,
            max_tokens=max_tokens or config.MAX_TOKENS,
            system=system_prompt,
            messages=validated_messages,
            temperature=temperature,
        )
        return response.content[0].text
    except anthropic.RateLimitError:
        print("[WARN] Rate limited. Waiting 30 seconds...")
        time.sleep(30)
        return chat_with_context(system_prompt, messages, temperature, max_tokens)
    except Exception as e:
        print(f"[ERROR] AI call failed: {e}")
        raise


def structured_output(system_prompt: str, user_prompt: str,
                      temperature: float = 0.2,
                      max_tokens: int = None) -> dict:
    """
    Request JSON-structured output from Claude.
    Used for gap assessments, risk registers, evidence lists, etc.
    
    Args:
        system_prompt: System instructions
        user_prompt: Request that should produce JSON output
        temperature: Lower = more deterministic (good for structured data)
    
    Returns:
        dict: Parsed JSON response
    """
    enhanced_system = (
        system_prompt + 
        "\n\nCRITICAL: You MUST respond with valid JSON only. "
        "Do NOT include any text before or after the JSON. "
        "Do NOT wrap the JSON in markdown code blocks. "
        "Do NOT include ```json or ``` markers. "
        "Start your response with { or [ and end with } or ]."
    )

    result = chat(enhanced_system, user_prompt, temperature,
                  max_tokens=max_tokens or config.MAX_TOKENS)

    # Clean up common issues
    result = result.strip()
    
    # Remove markdown code blocks if Claude adds them anyway
    if result.startswith("```json"):
        result = result[7:]
    if result.startswith("```"):
        result = result[3:]
    if result.endswith("```"):
        result = result[:-3]
    result = result.strip()

    # Sometimes Claude adds a preamble like "Here is the JSON:"
    # Try to find the actual JSON
    if not result.startswith("{") and not result.startswith("["):
        # Find the first { or [
        json_start_brace = result.find("{")
        json_start_bracket = result.find("[")
        
        starts = [s for s in [json_start_brace, json_start_bracket] if s >= 0]
        if starts:
            result = result[min(starts):]
        else:
            raise ValueError(f"No JSON found in response: {result[:200]}")

    # Trim any trailing text after the JSON
    # Find matching closing bracket
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        # Try to find valid JSON by trimming from the end
        for end_pos in range(len(result), 0, -1):
            try:
                return json.loads(result[:end_pos])
            except json.JSONDecodeError:
                continue
        raise ValueError(f"Could not parse JSON from response: {result[:500]}")


def simple_ask(question: str, context: str = "") -> str:
    """
    Simple helper for quick one-off questions.
    No system prompt needed.
    """
    system = (
        "You are a senior GRC (Governance, Risk, and Compliance) consultant "
        "with 15+ years of experience across multiple frameworks including "
        "NIST CSF, ISO 27001, SOC 2, HIPAA, PCI DSS, and CMMC."
    )
    prompt = question
    if context:
        prompt = f"Context: {context}\n\nQuestion: {question}"

    return chat(system, prompt, temperature=0.3)