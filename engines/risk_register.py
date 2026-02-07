"""
engines/risk_register.py

Generates risk registers from gap assessment findings.
Converts gaps into formally documented risks with ratings and treatment plans.
"""

import json
from datetime import datetime
from utils.ai_client import structured_output, chat
import config


class RiskRegister:
    """
    Builds a risk register from gap assessment findings.

    Usage:
        risk_engine = RiskRegister(company_info)
        risks = risk_engine.generate_from_gap_assessment(gap_results)
        treatments = risk_engine.generate_risk_treatment_plans()
    """

    def __init__(self, company_info: dict):
        self.company = company_info
        self.risks = []

    def generate_from_gap_assessment(self, gap_results: list) -> list:
        """
        Convert gap assessment findings into formal risk register entries.

        Parameters:
        -----------
        gap_results : list
            Results from GapAssessment.run_interactive_assessment()

        Returns:
        --------
        list : Risk register entries.
        """
        # Only convert significant gaps (score below 4)
        significant_gaps = [r for r in gap_results
                           if r.get("score") and r["score"] < 4]

        if not significant_gaps:
            print("  [INFO] No significant gaps found (all scores 4+).")
            return []

        system_prompt = f"""You are a risk management expert creating formal risk register entries.

Company: {self.company['name']}
Industry: {self.company['industry']}
Size: {self.company['size']}

Convert the provided gap assessment findings into risk register entries.
Group related gaps into single risk entries where appropriate.

For each risk, provide a JSON object with these exact fields:
- risk_id: string (format "RISK-001", "RISK-002", etc.)
- risk_title: string (concise, descriptive title)
- risk_description: string (detailed description of the risk)
- risk_category: string ("Operational", "Technical", "Compliance", or "Strategic")
- threat_source: string (who/what could exploit this)
- vulnerability: string (the gap that creates the risk)
- impact_description: string (what could happen)
- likelihood: integer (1-5, where 1=Rare, 5=Almost Certain)
- impact: integer (1-5, where 1=Negligible, 5=Catastrophic)
- inherent_risk_score: integer (likelihood × impact)
- inherent_risk_level: string ("Critical" if score>=20, "High" if >=12, "Medium" if >=6, "Low" if <6)
- existing_controls: string (any current mitigations)
- residual_likelihood: integer (1-5, after existing controls)
- residual_impact: integer (1-5, after existing controls)
- residual_risk_score: integer (residual_likelihood × residual_impact)
- residual_risk_level: string (same thresholds as inherent)
- risk_treatment: string ("Mitigate", "Accept", "Transfer", or "Avoid")
- treatment_plan: string (specific actions to address the risk)
- risk_owner: string (suggested role/title)
- target_date: string (suggested completion date)
- related_control_ids: list of strings (the control IDs from the gap assessment)

Be realistic with risk ratings. Consider the {self.company['industry']} industry context.
Return as a JSON array."""

        user_prompt = f"""Convert these gap assessment findings into risk register entries:

{json.dumps(significant_gaps, indent=2)}

Group related findings. Generate comprehensive risk entries."""

        try:
            print("  🤖 Generating risk register from findings...")
            risks = structured_output(system_prompt, user_prompt,
                                      max_tokens=4096)

            # Handle various response formats
            if isinstance(risks, dict):
                for key in ["risks", "risk_register", "entries", "data"]:
                    if key in risks:
                        risks = risks[key]
                        break
                else:
                    risks = [risks]

            if not isinstance(risks, list):
                risks = [risks]

            self.risks = risks
            print(f"  [OK] Generated {len(risks)} risk entries.")
            return risks

        except Exception as e:
            print(f"  [ERROR] Risk register generation failed: {e}")
            return []

    def generate_risk_treatment_plans(self) -> str:
        """Generate detailed treatment plans for high/critical risks."""

        high_risks = [r for r in self.risks
                      if r.get("inherent_risk_level") in ["Critical", "High"]]

        if not high_risks:
            return "No high or critical risks identified. All risks are Medium or Low."

        system_prompt = f"""You are a risk management expert creating detailed risk treatment plans
for {self.company['name']} ({self.company['industry']}).

For each risk, provide a comprehensive treatment plan including:

1. RISK SUMMARY
2. SPECIFIC MITIGATION ACTIONS (numbered, detailed steps)
3. IMPLEMENTATION TIMELINE (with milestones)
4. RESOURCE REQUIREMENTS (people, tools, budget estimates)
5. SUCCESS CRITERIA / KPIs (how to measure if the risk is being reduced)
6. MONITORING APPROACH (ongoing monitoring after treatment)
7. ESCALATION TRIGGERS (when to escalate if treatment isn't working)

Be specific and actionable. Include estimated costs where possible."""

        user_prompt = f"""Create detailed treatment plans for these high/critical risks:

{json.dumps(high_risks, indent=2)}"""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4000)