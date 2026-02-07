"""
engines/control_mapper.py

Maps controls between different compliance frameworks.
Useful when a client needs to comply with multiple frameworks
and wants to know where they overlap.
"""

import json
from utils.ai_client import chat


class ControlMapper:
    """
    Maps controls between compliance frameworks.

    Usage:
        mapper = ControlMapper(company_info)
        mapping = mapper.map_frameworks("NIST CSF 2.0", "ISO 27001:2022")
    """

    def __init__(self, company_info: dict):
        self.company = company_info

    def map_frameworks(self, source_framework: str,
                       target_framework: str) -> str:
        """
        Create a mapping between two frameworks.

        Parameters:
        -----------
        source_framework : str
            The framework you're mapping FROM.
        target_framework : str
            The framework you're mapping TO.

        Returns:
        --------
        str : Detailed mapping analysis.
        """
        system_prompt = """You are a GRC expert specializing in framework mapping and 
cross-framework control analysis.

Create a detailed, accurate control mapping between two frameworks.
For each major control area in the source framework, identify:

1. Source Control ID and Description
2. Corresponding Target Control ID(s) and Description(s)
3. Coverage Level: "Full Match", "Partial Match", or "No Direct Mapping"
4. Gap Notes: What the target requires that the source doesn't cover (or vice versa)

Organize by the source framework's structure.
Include a summary section at the end with:
- Total controls mapped
- Coverage statistics
- Unique requirements in each framework
- Recommendations for organizations complying with both"""

        user_prompt = f"""Create a control mapping from {source_framework} to {target_framework}.

This is for {self.company['name']} ({self.company['industry']}) 
who needs to comply with both frameworks.

Map all major control domains. Be thorough and accurate."""

        return chat(system_prompt, user_prompt, temperature=0.2, max_tokens=4096)

    def identify_unified_controls(self, frameworks: list) -> str:
        """
        Create a unified control set that satisfies multiple frameworks at once.
        This saves clients from implementing duplicate controls.
        """
        system_prompt = """You are a GRC architect designing a unified control framework.

Analyze multiple compliance frameworks and create a SINGLE consolidated 
control set that satisfies ALL of them simultaneously.

For each unified control, provide:
1. Unified Control ID (format: UC-XX-XXX)
2. Control Name
3. Control Description
4. Source Mappings (which control from each framework it satisfies)
5. Implementation Guidance
6. Evidence Requirements (what an auditor would want to see)

This helps organizations "implement once, comply many" — reducing 
duplicate effort across multiple compliance programs."""

        user_prompt = f"""Create a unified control framework for {self.company['name']} 
({self.company['industry']}) that satisfies ALL of these frameworks simultaneously:

{json.dumps(frameworks, indent=2)}

Focus on the most common and critical control areas.
Show the mapping from each unified control back to each source framework."""

        return chat(system_prompt, user_prompt, temperature=0.3, max_tokens=4096)