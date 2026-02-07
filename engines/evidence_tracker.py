"""
Evidence Tracker
Track evidence collection status for each control.
Essential for audit preparation.
"""

import json
import os
from datetime import datetime
from utils.ai_client import chat, structured_output
import config


class EvidenceTracker:
    def __init__(self, company_info: dict, framework_name: str):
        self.company = company_info
        self.framework = framework_name
        self.evidence_items = []

    def generate_evidence_requirements(self, controls: list = None) -> list:
        """
        Generate a comprehensive list of evidence needed for each control.
        """
        system_prompt = f"""You are a GRC auditor preparing an evidence request list for 
a {self.framework} assessment of {self.company['name']} ({self.company['industry']}).

For each control, identify the SPECIFIC evidence artifacts an auditor would 
expect to see. Be practical and specific.

For each evidence item, provide:
- evidence_id: string (format: EV-XXX)
- control_id: string (the framework control it satisfies)
- evidence_name: string (what the document/artifact is called)
- evidence_type: string (Policy/Procedure/Screenshot/Report/Configuration/Log/Record/Certificate/Contract)
- description: string (what specifically the auditor needs to see)
- typical_source: string (where this evidence usually comes from — e.g., "Okta Admin Console", "JIRA", "HR System")
- frequency: string (How often this should be collected — "Annual", "Quarterly", "Monthly", "Per Event", "Point-in-Time")
- priority: string ("Required", "Expected", "Nice-to-have")

Return as a JSON array."""

        if controls:
            control_text = json.dumps(controls[:30], indent=2)  # Limit for token size
        else:
            control_text = f"All major controls for {self.framework}"

        user_prompt = f"""Generate evidence requirements for these controls:

{control_text}

Company context:
- Industry: {self.company['industry']}
- Size: {self.company['size']}
- Description: {self.company['description']}

Be specific about what artifacts an auditor would request.
Return as a JSON array of evidence items."""

        try:
            results = structured_output(system_prompt, user_prompt)
            if isinstance(results, dict):
                results = results.get("evidence_items", results.get("evidence", [results]))
            if not isinstance(results, list):
                results = [results]

            # Add tracking fields
            for item in results:
                item["status"] = "Not Collected"
                item["collected_date"] = None
                item["file_path"] = None
                item["notes"] = ""
                item["reviewer"] = None

            self.evidence_items = results
            return results
        except Exception as e:
            print(f"[ERROR] Evidence generation failed: {e}")
            return []

    def update_evidence_status(self, evidence_id: str, status: str,
                                file_path: str = None, notes: str = ""):
        """Update the collection status of an evidence item."""
        valid_statuses = [
            "Not Collected", "Requested", "In Progress",
            "Collected", "Reviewed", "Approved", "N/A"
        ]

        if status not in valid_statuses:
            print(f"Invalid status. Use one of: {valid_statuses}")
            return

        for item in self.evidence_items:
            if item.get("evidence_id") == evidence_id:
                item["status"] = status
                item["file_path"] = file_path
                item["notes"] = notes
                if status == "Collected":
                    item["collected_date"] = datetime.now().isoformat()
                print(f"[UPDATED] {evidence_id}: {status}")
                return

        print(f"[ERROR] Evidence ID '{evidence_id}' not found.")

    def get_collection_summary(self) -> dict:
        """Get summary of evidence collection progress."""
        total = len(self.evidence_items)
        status_counts = {}
        for item in self.evidence_items:
            s = item.get("status", "Not Collected")
            status_counts[s] = status_counts.get(s, 0) + 1

        collected = status_counts.get("Collected", 0) + \
                    status_counts.get("Reviewed", 0) + \
                    status_counts.get("Approved", 0)

        return {
            "total_evidence_items": total,
            "collected": collected,
            "completion_percentage": round(collected / total * 100, 1) if total > 0 else 0,
            "status_breakdown": status_counts,
            "outstanding": [
                item for item in self.evidence_items
                if item.get("status") in ["Not Collected", "Requested"]
            ]
        }

    def generate_evidence_request_email(self, recipient_role: str,
                                         evidence_ids: list = None) -> str:
        """Generate a professional evidence request email."""

        if evidence_ids:
            items = [i for i in self.evidence_items
                     if i.get("evidence_id") in evidence_ids]
        else:
            items = [i for i in self.evidence_items
                     if i.get("status") in ["Not Collected", "Requested"]]

        system_prompt = """You are a GRC consultant writing a professional evidence request 
email. Be clear, polite, and specific about what is needed. 
Include deadlines and explain why each item is needed."""

        evidence_list = "\n".join([
            f"- {i.get('evidence_id')}: {i.get('evidence_name')} — {i.get('description')} "
            f"(Source: {i.get('typical_source', 'N/A')})"
            for i in items
        ])

        user_prompt = f"""Write a professional evidence request email to: {recipient_role}

Company: {self.company['name']}
Framework: {self.framework}

Evidence items needed:
{evidence_list}

Make it professional, clear, and include a reasonable deadline (2 weeks from now).
Include instructions on how to securely share the evidence."""

        return chat(system_prompt, user_prompt, temperature=0.4, max_tokens=2000)

    def save_tracker(self, output_dir: str = None):
        """Save evidence tracker to JSON."""
        output_dir = output_dir or config.REPORT_DIR
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(
            output_dir,
            f"evidence_tracker_{self.company['name'].replace(' ', '_')}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        output = {
            "metadata": {
                "company": self.company,
                "framework": self.framework,
                "generated": datetime.now().isoformat(),
                "summary": self.get_collection_summary()
            },
            "evidence_items": self.evidence_items
        }

        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)

        print(f"[SAVED] Evidence tracker: {filepath}")
        return filepath