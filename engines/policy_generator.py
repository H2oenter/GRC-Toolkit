"""
engines/policy_generator.py

Generates professional security policies and procedures.
This replaces hours of manual policy writing with AI-generated
first drafts that you can review and customize.
"""

import json
import os
from datetime import datetime
from utils.ai_client import chat
import config


# Common policies and which frameworks need them
POLICY_CATALOG = {
    "Information Security Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "SOC 2", "HIPAA", "PCI DSS"],
        "description": "Overarching information security policy",
    },
    "Access Control Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "SOC 2", "HIPAA", "PCI DSS"],
        "description": "Manages user access and authentication",
    },
    "Acceptable Use Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "SOC 2"],
        "description": "Defines acceptable use of company resources",
    },
    "Incident Response Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "SOC 2", "HIPAA", "PCI DSS"],
        "description": "Incident detection, response, and recovery",
    },
    "Data Classification Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "HIPAA", "PCI DSS"],
        "description": "Classifying and handling data based on sensitivity",
    },
    "Business Continuity Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "SOC 2"],
        "description": "Ensuring business continuity and disaster recovery",
    },
    "Change Management Policy": {
        "frameworks": ["ISO 27001", "SOC 2", "PCI DSS"],
        "description": "Managing changes to IT systems and infrastructure",
    },
    "Vendor Management Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "SOC 2", "HIPAA"],
        "description": "Third-party risk management",
    },
    "Encryption Policy": {
        "frameworks": ["ISO 27001", "HIPAA", "PCI DSS"],
        "description": "Encryption standards for data at rest and in transit",
    },
    "Physical Security Policy": {
        "frameworks": ["ISO 27001", "HIPAA", "PCI DSS"],
        "description": "Physical access and environmental controls",
    },
    "Risk Management Policy": {
        "frameworks": ["ISO 27001", "NIST CSF", "SOC 2"],
        "description": "Risk identification, assessment, and treatment",
    },
    "Privacy Policy": {
        "frameworks": ["HIPAA", "GDPR", "SOC 2"],
        "description": "Personal data protection and privacy rights",
    },
}


class PolicyGenerator:
    """
    Generates policies and procedures using Claude.

    Usage:
        gen = PolicyGenerator(company_info)
        policy = gen.generate_policy("Access Control Policy", framework="SOC 2 Type II")
        gen.save_document(policy, "policy", "Access Control Policy")
    """

    def __init__(self, company_info: dict):
        self.company = company_info

    def generate_policy(self, policy_type: str, framework: str = None,
                        additional_context: str = "",
                        custom_requirements: str = "") -> str:
        """
        Generate a complete, professional policy document.

        Parameters:
        -----------
        policy_type : str
            Name of the policy (e.g., "Access Control Policy")

        framework : str, optional
            Framework to align with (e.g., "SOC 2 Type II")

        additional_context : str, optional
            Extra info (e.g., "We use AWS and Okta")

        custom_requirements : str, optional
            Specific things to include

        Returns:
        --------
        str : The complete policy document in markdown format.
        """
        system_prompt = f"""You are a senior GRC consultant and policy writer with 15+ years 
of experience creating information security policies for enterprise organizations.

You are writing a policy for:
- Company Name: {self.company['name']}
- Industry: {self.company['industry']}
- Company Size: {self.company['size']}  
- Company Description: {self.company['description']}

Write a COMPLETE, PROFESSIONAL, READY-TO-USE policy document.

REQUIRED DOCUMENT STRUCTURE (follow this exactly):

1. DOCUMENT CONTROL
   - Policy Title
   - Policy Number (use format: POL-SEC-XXX)
   - Version: 1.0
   - Effective Date: [Current Date]
   - Last Review Date: [Current Date]
   - Next Review Date: [One year from now]
   - Policy Owner: [Suggest appropriate role]
   - Approved By: [Suggest appropriate role]

2. PURPOSE
   - Clear statement of why this policy exists

3. SCOPE
   - Who and what this policy applies to
   - Any explicit exclusions

4. DEFINITIONS
   - Key terms used in the policy (at least 5-8 terms)

5. POLICY STATEMENTS
   - Numbered, specific, auditable policy statements
   - Each statement should be measurable (an auditor could verify it)
   - Group by logical sections with headers
   - Include at least 15-20 specific policy statements

6. ROLES AND RESPONSIBILITIES
   - Specific roles and what each is responsible for
   - Include: Executive Leadership, CISO/Security Team, IT Department, 
     Department Managers, All Employees, Third Parties

7. ENFORCEMENT AND COMPLIANCE
   - How compliance will be measured
   - Consequences of non-compliance
   - Exception/waiver process

8. RELATED DOCUMENTS
   - List related policies, procedures, and standards

9. REVISION HISTORY
   - Version history table

WRITING GUIDELINES:
- Use professional, authoritative tone
- Be specific — avoid vague language like "appropriate" or "reasonable" without definition
- Every policy statement should be auditable
- Include specific timeframes, frequencies, and thresholds where applicable
- Reference industry best practices"""

        # Build the user prompt with optional elements
        parts = [f'Generate a complete "{policy_type}" for {self.company["name"]}.']

        if framework:
            parts.append(f"\nAlign this policy with: {framework}")
        if additional_context:
            parts.append(f"\nAdditional context about the organization: {additional_context}")
        if custom_requirements:
            parts.append(f"\nSpecific requirements to include: {custom_requirements}")

        parts.append("\nMake it comprehensive, specific, and ready for executive review.")

        user_prompt = "\n".join(parts)

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)

    def generate_procedure(self, procedure_name: str,
                           related_policy: str = "",
                           additional_context: str = "") -> str:
        """
        Generate a detailed, step-by-step procedure document.

        Parameters:
        -----------
        procedure_name : str
            Name of the procedure (e.g., "Incident Response Procedure")

        related_policy : str, optional
            The parent policy this procedure supports.

        additional_context : str, optional
            Extra info about tools, team structure, etc.
        """
        system_prompt = f"""You are a senior GRC consultant creating an operational procedure document
for {self.company['name']} ({self.company['industry']}, {self.company['size']}).

Write a DETAILED, STEP-BY-STEP procedure that any employee in the relevant role 
can follow independently.

REQUIRED DOCUMENT STRUCTURE:

1. DOCUMENT CONTROL
   - Procedure Title, ID (format: PROC-SEC-XXX), Version, Owner, Related Policy

2. PURPOSE
   - What this procedure accomplishes

3. SCOPE
   - Who performs this procedure and when

4. PREREQUISITES
   - Tools or systems needed
   - Access or permissions required
   - Knowledge or training required

5. DEFINITIONS
   - Key terms

6. PROCEDURE STEPS
   - Numbered main steps with sub-steps (1, 1.1, 1.2, etc.)
   - For each step include:
     * WHO performs it (role)
     * WHAT they do (specific action)
     * HOW they do it (detailed instructions)
     * EXPECTED OUTCOME
   - Include decision points: "IF [condition] THEN [action] ELSE [action]"
   - Include verification steps ("Confirm that...")

7. ESCALATION PATH
   - When and how to escalate
   - Contact information format

8. EXCEPTIONS AND EDGE CASES
   - Common exceptions and how to handle them

9. VERIFICATION / QUALITY CHECK
   - How to verify the procedure was completed correctly

10. RELATED DOCUMENTS

11. REVISION HISTORY

Make it detailed enough that a new employee on their first day could follow it."""

        parts = [f'Create a detailed procedure for: "{procedure_name}"']
        if related_policy:
            parts.append(f"\nThis supports the parent policy: {related_policy}")
        if additional_context:
            parts.append(f"\nAdditional context: {additional_context}")

        user_prompt = "\n".join(parts)

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)

    def identify_required_policies(self, framework: str,
                                   existing_policies: list = None) -> str:
        """
        Analyze which policies/procedures are needed for framework compliance.
        """
        existing = existing_policies or []

        system_prompt = """You are a GRC consultant performing a documentation gap analysis.
Identify ALL required policies, procedures, standards, and guidelines 
needed for framework compliance."""

        user_prompt = f"""For {self.company['name']} ({self.company['industry']}) 
to comply with {framework}, identify all required documents.

Currently existing policies: {json.dumps(existing) if existing else 'None identified'}

For EACH required document, provide:
1. Document Name
2. Type (Policy / Procedure / Standard / Guideline / Plan)
3. Priority (Required / Strongly Recommended / Recommended)
4. Framework Controls/Clauses it addresses
5. Status: EXISTS / MISSING / NEEDS UPDATE (based on existing list)
6. Brief description of what it must cover (2-3 sentences)

Organize by priority level. Be thorough — missing a required document 
could result in an audit finding."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4000)

    def save_document(self, content: str, doc_type: str,
                      doc_name: str, output_dir: str = None) -> str:
        """
        Save a generated document to a file.

        Parameters:
        -----------
        content : str
            The document content.
        doc_type : str
            "policy" or "procedure"
        doc_name : str
            Name of the document (used in filename).

        Returns:
        --------
        str : Path to saved file.
        """
        if doc_type == "policy":
            output_dir = output_dir or config.POLICY_DIR
        else:
            output_dir = output_dir or config.PROCEDURE_DIR

        os.makedirs(output_dir, exist_ok=True)

        # Create safe filename
        safe_name = doc_name.replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{doc_type}_{safe_name}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  [SAVED] {doc_type.title()} → {filepath}")
        return filepath