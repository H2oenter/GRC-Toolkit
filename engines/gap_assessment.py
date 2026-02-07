"""
engines/gap_assessment.py

The Gap Assessment Engine.
This is the core of what you do as a GRC consultant — comparing an
organization's current state against a framework's requirements.

HOW IT WORKS:
1. Load the framework controls
2. For each control category, ask the user about current state
3. Send that info to Claude for evaluation
4. Claude returns maturity ratings, gaps, and recommendations
5. Results are saved and can be exported
"""

import json
import os
from datetime import datetime
from utils.ai_client import chat, structured_output
from utils.framework_loader import load_framework, get_all_controls
import config


class GapAssessment:
    """
    Runs a gap assessment for a company against a framework.

    Usage:
        assessment = GapAssessment(company_info, "NIST CSF 2.0")
        results = assessment.run_interactive_assessment()
        assessment.save_results()
    """

    def __init__(self, company_info: dict, framework_name: str):
        """
        Parameters:
        -----------
        company_info : dict
            Must have keys: name, industry, size, description

        framework_name : str
            Must match one of config.SUPPORTED_FRAMEWORKS
        """
        self.company = company_info
        self.framework_name = framework_name
        self.framework_data = load_framework(framework_name)
        self.controls = get_all_controls(self.framework_data)
        self.results = []
        self.timestamp = datetime.now().isoformat()

    def run_interactive_assessment(self) -> list:
        """
        Run the assessment interactively — asks you questions about each
        control area, then Claude evaluates the gaps.

        Returns:
        --------
        list : Assessment results for all controls.
        """
        print(f"\n{'='*60}")
        print(f"  GAP ASSESSMENT: {self.framework_name}")
        print(f"  Company: {self.company['name']}")
        print(f"  Industry: {self.company['industry']}")
        print(f"{'='*60}")

        # If no framework file was loaded, use AI-only mode
        if not self.controls:
            print("\n[INFO] No framework file found. Using AI-generated controls.")
            return self._run_ai_only_assessment()

        # Group controls by category
        categories = {}
        for ctrl in self.controls:
            cat_key = ctrl["category_id"]
            if cat_key not in categories:
                categories[cat_key] = {
                    "function": ctrl["function"],
                    "function_id": ctrl["function_id"],
                    "category": ctrl["category"],
                    "category_id": ctrl["category_id"],
                    "controls": [],
                }
            categories[cat_key]["controls"].append(ctrl)

        total_categories = len(categories)
        current_cat = 0

        # Go through each category
        for cat_id, cat_data in categories.items():
            current_cat += 1
            print(f"\n{'─'*60}")
            print(f"  [{current_cat}/{total_categories}] "
                  f"{cat_data['function_id']}: {cat_data['function']}")
            print(f"  Category: {cat_data['category']} ({cat_data['category_id']})")
            print(f"{'─'*60}")

            # Show the controls in this category
            print("\n  Controls in this area:")
            for ctrl in cat_data["controls"]:
                print(f"    • {ctrl['control_id']}: {ctrl['description']}")

            # Ask user about current state
            print(f"\n  Describe your CURRENT state for this area.")
            print(f"  (What tools, processes, policies, controls exist?)")
            print(f"  (Type 'skip' to skip, 'none' if nothing exists)")
            print()

            current_state = input("  Your answer: ").strip()

            # Handle skip
            if current_state.lower() == "skip":
                for ctrl in cat_data["controls"]:
                    self.results.append({
                        "control_id": ctrl["control_id"],
                        "control_description": ctrl["description"],
                        "function": ctrl["function"],
                        "function_id": ctrl["function_id"],
                        "category": ctrl["category"],
                        "category_id": ctrl["category_id"],
                        "maturity": "Not Assessed",
                        "score": None,
                        "current_state_assessment": "Skipped by assessor",
                        "gap": "Not assessed",
                        "recommendations": "Needs manual assessment",
                        "priority": "N/A",
                        "estimated_effort": "N/A",
                    })
                print("  ⏩ Skipped.")
                continue

            if current_state.lower() == "none":
                current_state = "Nothing exists. No tools, no processes, no policies, no controls in this area."

            # Send to Claude for evaluation
            print("\n  🤖 Analyzing with Claude...")
            assessment_results = self._evaluate_category(cat_data, current_state)
            self.results.extend(assessment_results)

            # Show results
            print("\n  Results:")
            for item in assessment_results:
                icon = {
                    "Fully Implemented": "✅",
                    "Largely Implemented": "🟢",
                    "Partially Implemented": "🟡",
                    "Minimally Implemented": "🟠",
                    "Not Implemented": "🔴",
                }.get(item.get("maturity", ""), "⬜")

                score = item.get("score", "?")
                print(f"    {icon} {item.get('control_id', 'N/A')}: "
                      f"{item.get('maturity', 'Unknown')} ({score}/5)")

        print(f"\n{'='*60}")
        print(f"  Assessment complete! {len(self.results)} controls assessed.")
        print(f"{'='*60}")

        return self.results

    def _run_ai_only_assessment(self) -> list:
        """
        When no framework JSON file exists, Claude generates the controls
        and does the assessment based on its knowledge.
        """
        system_prompt = f"""You are a senior GRC consultant performing a gap assessment 
against {self.framework_name}.

Company: {self.company['name']}
Industry: {self.company['industry']}
Size: {self.company['size']}
Description: {self.company['description']}

Generate the key control areas for {self.framework_name} and assess them 
based on the user's description of their current security posture.

For each control, provide:
- control_id: the framework's control identifier
- control_description: what the control requires
- function: the parent function/domain
- category: the category name
- maturity: one of "Not Implemented", "Minimally Implemented", "Partially Implemented", "Largely Implemented", "Fully Implemented"
- score: 1-5 integer
- current_state_assessment: what they currently have
- gap: what's missing
- recommendations: specific actions to close the gap
- priority: "Critical", "High", "Medium", or "Low"
- estimated_effort: "Quick Win", "Short-term", "Medium-term", or "Long-term"

Respond as a JSON array."""

        print("\nDescribe your organization's overall security posture.")
        print("Include: tools used, policies in place, team structure,")
        print("recent security initiatives, known gaps, etc.")
        print("(The more detail you provide, the better the assessment)\n")

        current_state = input("Your description:\n> ").strip()

        user_prompt = f"""Based on this description of the organization's current state, 
perform a gap assessment against the key controls in {self.framework_name}:

{current_state}

Assess at least 20 key controls. Return as a JSON array."""

        print("\n🤖 Claude is performing the assessment... (this may take a minute)")

        try:
            results = structured_output(system_prompt, user_prompt,
                                        max_tokens=4096)
            if isinstance(results, dict):
                results = results.get("assessments", results.get("controls", [results]))
            if not isinstance(results, list):
                results = [results]
            self.results = results
            return results
        except Exception as e:
            print(f"[ERROR] Assessment failed: {e}")
            return []

    def _evaluate_category(self, category_data: dict,
                           current_state: str) -> list:
        """
        Send a control category to Claude for evaluation.

        Parameters:
        -----------
        category_data : dict
            The category info including its controls.

        current_state : str
            The user's description of their current state for this area.

        Returns:
        --------
        list : Assessment results for each control in the category.
        """
        system_prompt = f"""You are an expert GRC consultant performing a gap assessment 
against {self.framework_name} for the following organization:

Company: {self.company['name']}
Industry: {self.company['industry']}
Size: {self.company['size']}
Description: {self.company['description']}

Evaluate the organization's current state against EACH control listed below.
Be specific, realistic, and actionable in your assessments.

MATURITY LEVELS (use these exactly):
- "Not Implemented" (Score: 1) — No evidence of the control existing
- "Minimally Implemented" (Score: 2) — Ad hoc, inconsistent, reactive
- "Partially Implemented" (Score: 3) — Defined but not fully deployed or enforced
- "Largely Implemented" (Score: 4) — Implemented with minor gaps
- "Fully Implemented" (Score: 5) — Fully operational, monitored, and continuously improved

For each control, respond with a JSON array of objects. Each object must have:
- control_id: string
- control_description: string
- maturity: string (one of the levels above, exactly as written)
- score: integer (1-5)
- current_state_assessment: string (what they currently have based on their description)
- gap: string (what's missing or needs improvement)
- recommendations: string (specific, actionable steps to close the gap)
- priority: string ("Critical", "High", "Medium", or "Low")
- estimated_effort: string ("Quick Win", "Short-term", "Medium-term", or "Long-term")"""

        controls_text = "\n".join(
            [f"- {c['control_id']}: {c['description']}"
             for c in category_data["controls"]]
        )

        user_prompt = f"""Assess these controls in the "{category_data['category']}" category:

CONTROLS:
{controls_text}

ORGANIZATION'S CURRENT STATE FOR THIS AREA:
{current_state}

Return your assessment as a JSON array with one object per control."""

        try:
            results = structured_output(system_prompt, user_prompt)

            # Handle various response formats Claude might use
            if isinstance(results, dict):
                # Claude might wrap it in a key
                for key in ["assessments", "controls", "results", "data"]:
                    if key in results:
                        results = results[key]
                        break
                else:
                    # Single result, wrap in list
                    results = [results]

            if not isinstance(results, list):
                results = [results]

            # Add category metadata to each result
            for item in results:
                item["function"] = category_data["function"]
                item["function_id"] = category_data["function_id"]
                item["category"] = category_data["category"]
                item["category_id"] = category_data["category_id"]

            return results

        except Exception as e:
            print(f"  [ERROR] Failed to assess {category_data['category_id']}: {e}")
            # Return placeholder results so we don't lose the category
            return [{
                "control_id": c["control_id"],
                "control_description": c["description"],
                "function": category_data["function"],
                "function_id": category_data["function_id"],
                "category": category_data["category"],
                "category_id": category_data["category_id"],
                "maturity": "Not Assessed",
                "score": 0,
                "current_state_assessment": current_state,
                "gap": f"Automated assessment failed: {e}",
                "recommendations": "Requires manual assessment",
                "priority": "High",
                "estimated_effort": "Unknown",
            } for c in category_data["controls"]]

    def generate_executive_summary(self) -> str:
        """Generate an executive summary of the entire assessment."""

        # Calculate statistics
        total = len(self.results)
        assessed = [r for r in self.results
                    if r.get("score") and r.get("score") > 0]
        avg_score = (sum(r["score"] for r in assessed) / len(assessed)
                     if assessed else 0)

        maturity_counts = {}
        priority_counts = {}
        for r in self.results:
            mat = r.get("maturity", "Not Assessed")
            pri = r.get("priority", "N/A")
            maturity_counts[mat] = maturity_counts.get(mat, 0) + 1
            priority_counts[pri] = priority_counts.get(pri, 0) + 1

        system_prompt = """You are a senior GRC consultant writing an executive summary 
for a board-level gap assessment report. Write professionally and concisely.

Structure your summary as:
1. EXECUTIVE OVERVIEW (2-3 paragraphs)
2. KEY STRENGTHS (bullet points)
3. CRITICAL GAPS REQUIRING IMMEDIATE ATTENTION (bullet points with control IDs)
4. MATURITY SCORE OVERVIEW (interpret the numbers)
5. TOP 5 STRATEGIC RECOMMENDATIONS (numbered, with brief justification)
6. SUGGESTED ROADMAP OVERVIEW (3-4 phases with timelines)

Use professional GRC language appropriate for executive leadership."""

        user_prompt = f"""Generate an executive summary for this gap assessment:

ASSESSMENT DETAILS:
- Framework: {self.framework_name}
- Company: {self.company['name']}
- Industry: {self.company['industry']}
- Company Size: {self.company['size']}
- Assessment Date: {self.timestamp}

STATISTICS:
- Total Controls Assessed: {total}
- Average Maturity Score: {avg_score:.1f} / 5.0
- Maturity Distribution: {json.dumps(maturity_counts, indent=2)}
- Priority Distribution: {json.dumps(priority_counts, indent=2)}

DETAILED FINDINGS:
{json.dumps(self.results, indent=2)}"""

        return chat(system_prompt, user_prompt, temperature=0.4, max_tokens=4000)

    def get_remediation_roadmap(self) -> str:
        """Generate a prioritized remediation roadmap."""

        # Only include items that need work
        gaps = [r for r in self.results
                if r.get("score") and r["score"] < 4]

        if not gaps:
            return "All controls are Largely or Fully Implemented. No remediation needed."

        system_prompt = """You are a GRC consultant creating a remediation roadmap.

Organize all recommendations into clear phases:
- Phase 1 — IMMEDIATE (0-30 days): Critical findings and quick wins
- Phase 2 — SHORT-TERM (30-90 days): High priority items
- Phase 3 — MEDIUM-TERM (90-180 days): Medium priority improvements  
- Phase 4 — LONG-TERM (180-365 days): Optimization and maturity improvements

For each item in the roadmap, include:
- Control ID
- Gap Summary
- Specific Action Required
- Suggested Owner (role, not person)
- Estimated Level of Effort (hours/days)
- Dependencies (if any)
- Success Criteria

End with a budget estimation section and resource requirements summary."""

        user_prompt = f"""Create a remediation roadmap for {self.company['name']}.

Framework: {self.framework_name}
Industry: {self.company['industry']}

Findings requiring remediation (scored below 4/5):
{json.dumps(gaps, indent=2)}

Create a comprehensive, actionable roadmap."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4000)

    def save_results(self, output_dir: str = None) -> str:
        """
        Save assessment results to a JSON file.

        Returns:
        --------
        str : Path to the saved file.
        """
        output_dir = output_dir or config.GAP_ASSESSMENT_DIR
        os.makedirs(output_dir, exist_ok=True)

        safe_company = self.company["name"].replace(" ", "_").replace("/", "_")
        safe_framework = self.framework_name.replace(" ", "_").replace(":", "")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"gap_assessment_{safe_company}_{safe_framework}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        output = {
            "metadata": {
                "company": self.company,
                "framework": self.framework_name,
                "timestamp": self.timestamp,
                "total_controls": len(self.results),
                "assessed_controls": len([r for r in self.results if r.get("score")]),
            },
            "results": self.results,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"\n  [SAVED] Results → {filepath}")
        return filepath