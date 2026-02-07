"""
utils/framework_loader.py

Loads framework control data from JSON files.
If a framework file doesn't exist yet, it tells you
and falls back to AI-generated knowledge.
"""

import json
import os


def load_framework(framework_name: str) -> dict:
    """
    Load a framework's controls from a JSON file.

    Parameters:
    -----------
    framework_name : str
        Friendly name like "NIST CSF 2.0"

    Returns:
    --------
    dict : Framework data with functions, categories, and controls.
    """
    # Map friendly names to actual filenames
    framework_files = {
        "NIST CSF 2.0": "nist_csf.json",
        "ISO 27001:2022": "iso27001.json",
        "SOC 2 Type II": "soc2.json",
        "HIPAA": "hipaa.json",
        "PCI DSS 4.0": "pci_dss.json",
        "CMMC 2.0": "cmmc.json",
        "NIST 800-53 Rev 5": "nist_800_53.json",
        "CIS Controls v8": "cis_v8.json",
        "GDPR": "gdpr.json",
    }

    filename = framework_files.get(framework_name)
    if not filename:
        print(f"[WARNING] Framework '{framework_name}' not recognized.")
        print(f"  Available frameworks: {list(framework_files.keys())}")
        return {"framework": framework_name, "functions": [], "source": "ai_only"}

    filepath = os.path.join("frameworks", filename)

    if not os.path.exists(filepath):
        print(f"[INFO] Framework file not found: {filepath}")
        print(f"  The assessment will use Claude's built-in knowledge of {framework_name}.")
        print(f"  For better results, create {filepath} with the control data.")
        return {"framework": framework_name, "functions": [], "source": "ai_only"}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[OK] Loaded framework: {framework_name} from {filepath}")
    return data


def get_all_controls(framework_data: dict) -> list:
    """
    Flatten the hierarchical framework data into a flat list of controls.

    Returns:
    --------
    list : Each item is a dict with function, category, control_id, description.
    """
    controls = []
    for function in framework_data.get("functions", []):
        for category in function.get("categories", []):
            for sub in category.get("subcategories", []):
                controls.append({
                    "function": function["name"],
                    "function_id": function["id"],
                    "category": category["name"],
                    "category_id": category["id"],
                    "control_id": sub["id"],
                    "description": sub["description"],
                })
    return controls


def format_controls_for_prompt(controls: list) -> str:
    """
    Format a list of controls into readable text for Claude prompts.
    """
    lines = []
    current_function = ""
    for ctrl in controls:
        if ctrl["function"] != current_function:
            current_function = ctrl["function"]
            lines.append(f"\n## {ctrl['function_id']} - {ctrl['function']}")
        lines.append(f"  {ctrl['control_id']}: {ctrl['description']}")
    return "\n".join(lines)