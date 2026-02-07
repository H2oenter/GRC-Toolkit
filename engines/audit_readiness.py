"""
Audit Readiness Assessment
Evaluates overall readiness for an upcoming audit.
Combines gap assessment, evidence tracking, and policy review.
"""

from utils.ai_client import chat
import json
from datetime import datetime


class AuditReadinessAssessor:
    def __init__(self, company_info: dict, framework: str):
        self.company = company_info
        self.framework = framework

    def assess_readiness(self, gap_results: list = None,
                          evidence_summary: dict = None,
                          policy_list: list = None) -> str:
        """
        Comprehensive audit readiness assessment.
        """
        system_prompt = f"""You are a lead auditor preparing an organization for a 
{self.framework} audit. Assess their readiness based on the available information.

Provide a comprehensive readiness report with:

1. OVERALL READINESS SCORE (0-100%)
   - Break down by category

2. READINESS BY DOMAIN
   - For each major control domain, rate readiness (Red/Yellow/Green)
   - Identify specific blockers

3. CRITICAL PATH ITEMS
   - What MUST be done before the audit
   - Items that would result in audit failure if not addressed

4. AUDIT PREPARATION CHECKLIST
   - 30-day countdown checklist
   - Who needs to be involved
   - Documents that need to be ready

5. LIKELY AUDITOR QUESTIONS
   - Top 20 questions an auditor will ask
   - Suggested responses

6. RISK AREAS
   - Where the auditor is most likely to find issues
   - How to proactively address them

7. RECOMMENDATIONS
   - Quick wins (can be done in < 1 week)
   - Medium-term fixes (1-4 weeks)
   - Items to document as "planned improvements"

Company: {self.company['name']} ({self.company['industry']}, {self.company['size']})"""

        context_parts = []

        if gap_results:
            scored = [r for r in gap_results if r.get("score")]
            avg = sum(r["score"] for r in scored) / len(scored) if scored else 0
            critical_gaps = [r for r in gap_results
                           if r.get("score") and r["score"] <= 2]
            context_parts.append(f"""
GAP ASSESSMENT RESULTS:
- Average Maturity: {avg:.1f}/5.0
- Critical Gaps (score ≤ 2): {len(critical_gaps)}
- Top Critical Gaps: {json.dumps(critical_gaps[:10], indent=2)}""")

        if evidence_summary:
            context_parts.append(f"""
EVIDENCE COLLECTION STATUS:
{json.dumps(evidence_summary, indent=2)}""")

        if policy_list:
            context_parts.append(f"""
EXISTING POLICIES:
{json.dumps(policy_list, indent=2)}""")

        user_prompt = f"""Assess audit readiness for {self.framework}:

{''.join(context_parts) if context_parts else 'No prior assessment data available. Provide a general readiness framework and checklist.'}

Provide a comprehensive audit readiness report."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)

    def generate_audit_preparation_plan(self, audit_date: str,
                                         gap_results: list = None) -> str:
        """Generate a day-by-day audit preparation plan."""

        system_prompt = f"""You are a GRC consultant creating an audit preparation plan.
The audit date is {audit_date}. Create a detailed preparation timeline 
working backwards from the audit date.

Include:
- Weekly milestones
- Specific tasks with owners
- Document preparation requirements
- Mock audit / dry run schedule
- Day-of-audit logistics
- Post-audit follow-up plan

Company: {self.company['name']} ({self.company['industry']})
Framework: {self.framework}"""

        gap_context = ""
        if gap_results:
            critical = [r for r in gap_results if r.get("score", 5) <= 2]
            gap_context = f"\nCritical gaps to address: {json.dumps(critical[:10], indent=2)}"

        user_prompt = f"""Create an audit preparation plan.
Audit Date: {audit_date}
Framework: {self.framework}
{gap_context}

Create a detailed preparation timeline with specific tasks, owners, and deadlines."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)