"""
Document Review Engine
Upload existing policies/procedures and get AI-powered analysis:
- Gap identification against frameworks
- Quality assessment
- Improvement recommendations
- Compliance mapping
"""

import os
from utils.ai_client import chat, structured_output
from datetime import datetime
import config


class DocumentReviewer:
    def __init__(self, company_info: dict):
        self.company = company_info

    def read_document(self, file_path: str) -> str:
        """Read document from various formats."""
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        elif ext == ".docx":
            try:
                from docx import Document
                doc = Document(file_path)
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)
                return "\n".join(full_text)
            except ImportError:
                raise ImportError("python-docx required: pip install python-docx")

        elif ext == ".pdf":
            try:
                import PyPDF2
                text = []
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text.append(page.extract_text())
                return "\n".join(text)
            except ImportError:
                raise ImportError("PyPDF2 required: pip install PyPDF2")

        else:
            # Try reading as plain text
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

    def review_policy_against_framework(self, document_text: str,
                                         document_name: str,
                                         framework: str) -> dict:
        """
        Review an existing policy against a compliance framework.
        Returns structured findings.
        """
        system_prompt = f"""You are a senior GRC auditor reviewing an existing policy document 
for compliance with {framework}.

Company: {self.company['name']} ({self.company['industry']})

Perform a thorough review and provide:

1. DOCUMENT QUALITY ASSESSMENT
   - Overall quality score (1-10)
   - Structure and organization
   - Clarity and readability
   - Completeness

2. FRAMEWORK ALIGNMENT
   - Which {framework} controls this policy addresses
   - Coverage level for each control (Full/Partial/None)
   - Controls that should be addressed but aren't

3. CONTENT GAPS
   - Missing sections that are expected
   - Topics covered inadequately
   - Vague or unauditable statements

4. SPECIFIC FINDINGS
   For each finding:
   - Finding ID
   - Severity (Critical/High/Medium/Low/Informational)
   - Section/Area
   - Description of the issue
   - Specific recommendation
   - Reference to {framework} requirement

5. POSITIVE OBSERVATIONS
   - What the document does well
   - Strong sections

6. RECOMMENDED ACTIONS
   - Prioritized list of improvements
   - Specific language suggestions where applicable

Respond in JSON format."""

        user_prompt = f"""Review this document: "{document_name}"

DOCUMENT CONTENT:
---
{document_text[:12000]}
---

{"[NOTE: Document truncated to 12000 characters for analysis. Full document is longer.]" if len(document_text) > 12000 else ""}

Provide your comprehensive review in JSON format."""

        try:
            result = structured_output(system_prompt, user_prompt)
            result["document_name"] = document_name
            result["framework"] = framework
            result["review_date"] = datetime.now().isoformat()
            return result
        except Exception as e:
            # Fall back to text response
            text_result = chat(system_prompt, user_prompt, max_tokens=4096)
            return {
                "document_name": document_name,
                "framework": framework,
                "review_date": datetime.now().isoformat(),
                "review": text_result,
                "format": "text"
            }

    def review_policy_quality(self, document_text: str,
                               document_name: str) -> str:
        """
        General quality review of a policy (no specific framework).
        """
        system_prompt = f"""You are an expert policy writer and GRC consultant reviewing a 
policy document for quality and best practices.

Company: {self.company['name']} ({self.company['industry']})

Evaluate against these policy quality criteria:
1. Document Control: Does it have proper versioning, ownership, approval info?
2. Purpose: Is the purpose clearly stated?
3. Scope: Is the scope well-defined? Who does it apply to?
4. Definitions: Are key terms defined?
5. Policy Statements: Are they clear, specific, and auditable?
6. Roles & Responsibilities: Are they clearly assigned?
7. Compliance/Enforcement: Are consequences and monitoring defined?
8. Review Cycle: Is there a defined review cadence?
9. References: Are related documents referenced?
10. Language Quality: Is it professional, unambiguous, free of jargon?

For each criterion, provide:
- Score (1-5)
- Current state
- Specific recommendations for improvement
- Example improved language where applicable

Also provide an overall quality score and a prioritized improvement plan."""

        user_prompt = f"""Review this policy for quality: "{document_name}"

DOCUMENT:
---
{document_text[:12000]}
---

Provide a detailed quality assessment."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)

    def compare_policies(self, doc1_text: str, doc1_name: str,
                          doc2_text: str, doc2_name: str) -> str:
        """Compare two versions of a policy or two related policies."""

        system_prompt = """You are a GRC consultant comparing two policy documents.
Identify:
1. Key differences between the documents
2. What each document covers that the other doesn't
3. Conflicting statements
4. Which document is more comprehensive
5. Recommendations for consolidation or harmonization"""

        user_prompt = f"""Compare these two documents:

DOCUMENT 1: "{doc1_name}"
---
{doc1_text[:6000]}
---

DOCUMENT 2: "{doc2_name}"
---
{doc2_text[:6000]}
---

Provide a detailed comparison analysis."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)

    def generate_improvement_draft(self, document_text: str,
                                    document_name: str,
                                    review_findings: str) -> str:
        """
        Take an existing document and review findings,
        generate an improved version.
        """
        system_prompt = f"""You are a senior GRC policy writer. You've been given an existing 
policy document and review findings. Your job is to rewrite/improve the policy 
addressing all the findings while maintaining the original intent and company voice.

Company: {self.company['name']} ({self.company['industry']})

Guidelines:
- Maintain the original structure where it's good
- Add missing sections
- Make vague statements specific and auditable
- Add proper document control information
- Ensure all policy statements are numbered and actionable
- Keep the professional tone consistent"""

        user_prompt = f"""Improve this policy based on the review findings:

ORIGINAL DOCUMENT: "{document_name}"
---
{document_text[:8000]}
---

REVIEW FINDINGS:
---
{review_findings[:4000]}
---

Generate the improved version of this policy document."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)

    def save_review(self, review_data, document_name: str,
                     output_dir: str = None):
        """Save review results."""
        output_dir = output_dir or config.REPORT_DIR
        os.makedirs(output_dir, exist_ok=True)

        filename = (f"review_{document_name.replace(' ', '_')}_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        import json

        if isinstance(review_data, dict):
            filepath = os.path.join(output_dir, filename + ".json")
            with open(filepath, "w") as f:
                json.dump(review_data, f, indent=2)
        else:
            filepath = os.path.join(output_dir, filename + ".md")
            with open(filepath, "w") as f:
                f.write(str(review_data))

        print(f"[SAVED] Review saved to: {filepath}")
        return filepath