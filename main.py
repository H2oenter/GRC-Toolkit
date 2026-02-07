#!/usr/bin/env python3
"""
GRC Automation Toolkit — Command Line Interface
=================================================
Location: grc_toolkit/main.py

Run with: python main.py

Provides interactive CLI for:
1. Gap Assessments
2. Policy & Procedure Generation
3. Control Mapping
4. Document Review
5. Risk Register Generation
6. Evidence Tracking
7. Audit Readiness Assessment
"""

import os
import sys
import json
from datetime import datetime

# Create output directories on startup
for d in ["outputs/gap_assessments", "outputs/policies",
          "outputs/procedures", "outputs/reports", "frameworks"]:
    os.makedirs(d, exist_ok=True)

import config
from engines.gap_assessment import GapAssessment
from engines.policy_generator import PolicyGenerator, POLICY_CATALOG
from engines.risk_register import RiskRegister
from engines.control_mapper import ControlMapper
from engines.document_reviewer import DocumentReviewer
from engines.evidence_tracker import EvidenceTracker
from engines.audit_readiness import AuditReadinessAssessor
from utils.document_exporter import (
    export_gap_assessment_xlsx,
    export_risk_register_xlsx,
    export_evidence_tracker_xlsx,
)


# ══════════════════════════════════════════════════════
# SHARED INPUT HELPERS
# ══════════════════════════════════════════════════════

def get_company_info() -> dict:
    """Collect company information interactively."""
    print("\n" + "=" * 55)
    print("  📋 COMPANY INFORMATION")
    print("=" * 55)
    name = input("  Company Name: ").strip()
    industry = input("  Industry (e.g., Healthcare, Finance, Tech): ").strip()
    size = input("  Company Size (e.g., 50 employees, 500, 5000): ").strip()
    description = input("  Brief Description (what does the company do?): ").strip()

    company = {
        "name": name or "Acme Corp",
        "industry": industry or "Technology",
        "size": size or "200 employees",
        "description": description or "SaaS company providing cloud services",
    }
    print(f"\n  ✅ Company set: {company['name']} ({company['industry']})")
    return company


def select_framework() -> str:
    """Let user select a compliance framework."""
    print("\n  Available Frameworks:")
    for i, fw in enumerate(config.SUPPORTED_FRAMEWORKS, 1):
        print(f"    {i}. {fw}")

    choice = input("\n  Select framework (number): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(config.SUPPORTED_FRAMEWORKS):
            selected = config.SUPPORTED_FRAMEWORKS[idx]
            print(f"  ✅ Selected: {selected}")
            return selected
    except (ValueError, IndexError):
        pass

    print("  ⚠️  Invalid selection, defaulting to NIST CSF 2.0")
    return "NIST CSF 2.0"


def confirm(prompt: str) -> bool:
    """Simple y/n confirmation."""
    return input(f"\n  {prompt} (y/n): ").strip().lower() in ["y", "yes"]


def timestamp() -> str:
    """Return formatted timestamp for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ══════════════════════════════════════════════════════
# 1. GAP ASSESSMENT
# ══════════════════════════════════════════════════════

def run_gap_assessment():
    """Run the full gap assessment workflow."""
    print("\n" + "=" * 60)
    print("  🔍 GAP ASSESSMENT ENGINE")
    print("=" * 60)

    company = get_company_info()
    framework = select_framework()

    print(f"\n  Starting gap assessment for {company['name']} "
          f"against {framework}...")
    print("  For each control area, describe your current state.")
    print("  Type 'skip' to skip a domain, 'none' if nothing exists.\n")

    assessment = GapAssessment(company, framework)
    results = assessment.run_interactive_assessment()

    if not results:
        print("\n  ⚠️  No results generated.")
        return

    # Save raw JSON results
    json_path = assessment.save_results()

    # Generate executive summary
    if confirm("Generate Executive Summary?"):
        print("\n  ⏳ Generating Executive Summary...")
        summary = assessment.generate_executive_summary()

        summary_path = os.path.join(
            config.REPORT_DIR,
            f"executive_summary_{timestamp()}.md"
        )
        with open(summary_path, "w") as f:
            f.write(summary)
        print(f"  ✅ Saved: {summary_path}")
        print(f"\n{'─'*60}")
        print(summary[:2000])
        if len(summary) > 2000:
            print("  ...[see full file for complete summary]")
        print(f"{'─'*60}")

    # Generate remediation roadmap
    if confirm("Generate Remediation Roadmap?"):
        print("\n  ⏳ Generating Remediation Roadmap...")
        roadmap = assessment.get_remediation_roadmap()

        roadmap_path = os.path.join(
            config.REPORT_DIR,
            f"remediation_roadmap_{timestamp()}.md"
        )
        with open(roadmap_path, "w") as f:
            f.write(roadmap)
        print(f"  ✅ Saved: {roadmap_path}")

    # Export to Excel
    if confirm("Export results to Excel?"):
        xlsx_path = os.path.join(
            config.GAP_ASSESSMENT_DIR,
            f"gap_assessment_{timestamp()}.xlsx"
        )
        metadata = {
            "company": company,
            "framework": framework,
            "timestamp": datetime.now().isoformat(),
        }
        export_gap_assessment_xlsx(results, metadata, xlsx_path)

    # Generate risk register from findings
    if confirm("Generate Risk Register from findings?"):
        print("\n  ⏳ Generating Risk Register...")
        risk_engine = RiskRegister(company)
        risks = risk_engine.generate_from_gap_assessment(results)

        if risks:
            # Save JSON
            risk_json_path = os.path.join(
                config.REPORT_DIR,
                f"risk_register_{timestamp()}.json"
            )
            with open(risk_json_path, "w") as f:
                json.dump({"risks": risks}, f, indent=2)
            print(f"  ✅ Saved: {risk_json_path}")

            # Save Excel
            risk_xlsx_path = os.path.join(
                config.REPORT_DIR,
                f"risk_register_{timestamp()}.xlsx"
            )
            export_risk_register_xlsx(risks, company["name"], risk_xlsx_path)

            # Treatment plans
            if confirm("Generate Risk Treatment Plans?"):
                print("\n  ⏳ Generating Treatment Plans...")
                treatments = risk_engine.generate_risk_treatment_plans()
                treatment_path = os.path.join(
                    config.REPORT_DIR,
                    f"risk_treatment_plans_{timestamp()}.md"
                )
                with open(treatment_path, "w") as f:
                    f.write(treatments)
                print(f"  ✅ Saved: {treatment_path}")

    print("\n  ✅ Gap Assessment Complete!")
    print(f"  📁 All outputs saved to: {config.OUTPUT_DIR}/")


# ══════════════════════════════════════════════════════
# 2. POLICY & PROCEDURE GENERATOR
# ══════════════════════════════════════════════════════

def run_policy_generator():
    """Run the policy/procedure generation workflow."""
    print("\n" + "=" * 60)
    print("  📋 POLICY & PROCEDURE GENERATOR")
    print("=" * 60)

    company = get_company_info()
    generator = PolicyGenerator(company)

    while True:
        print("\n  ┌─────────────────────────────────────┐")
        print("  │  Policy Generator Options            │")
        print("  ├─────────────────────────────────────┤")
        print("  │  1. Generate a Single Policy         │")
        print("  │  2. Generate a Procedure             │")
        print("  │  3. Identify Required Policies       │")
        print("  │  4. Generate Full Policy Suite       │")
        print("  │  5. Back to Main Menu                │")
        print("  └─────────────────────────────────────┘")

        choice = input("\n  Select option: ").strip()

        if choice == "1":
            # Single Policy
            print("\n  Available Policy Types:")
            policy_names = list(POLICY_CATALOG.keys())
            for i, name in enumerate(policy_names, 1):
                print(f"    {i}. {name}")
            print(f"    {len(policy_names)+1}. ✏️  Custom (type your own)")

            pol_choice = input("\n  Select policy type: ").strip()
            try:
                idx = int(pol_choice) - 1
                if 0 <= idx < len(policy_names):
                    policy_name = policy_names[idx]
                else:
                    policy_name = input("  Enter custom policy name: ").strip()
            except (ValueError, IndexError):
                policy_name = input("  Enter policy name: ").strip()

            if not policy_name:
                print("  ⚠️  No policy name provided.")
                continue

            framework = input("  Align with framework? (Enter name or press Enter to skip): ").strip()
            context = input("  Additional context (optional): ").strip()

            print(f"\n  ⏳ Generating {policy_name}...")
            content = generator.generate_policy(
                policy_name,
                framework=framework or None,
                additional_context=context or "",
            )

            # Preview
            print(f"\n{'─'*60}")
            print(content[:3000])
            if len(content) > 3000:
                print("\n  ...[truncated — see full file]")
            print(f"{'─'*60}")

            # Save
            path = generator.save_document(content, "policy", policy_name)

        elif choice == "2":
            # Procedure
            proc_name = input("\n  Procedure name: ").strip()
            if not proc_name:
                print("  ⚠️  No name provided.")
                continue

            related_policy = input("  Related policy (optional): ").strip()
            context = input("  Additional context (optional): ").strip()

            print(f"\n  ⏳ Generating: {proc_name}...")
            content = generator.generate_procedure(
                proc_name,
                related_policy=related_policy,
                additional_context=context,
            )

            print(f"\n{'─'*60}")
            print(content[:3000])
            if len(content) > 3000:
                print("\n  ...[truncated]")
            print(f"{'─'*60}")

            path = generator.save_document(content, "procedure", proc_name)

        elif choice == "3":
            # Required policies analysis
            framework = select_framework()
            existing = input("  Existing policies (comma-separated, or Enter): ").strip()
            existing_list = ([p.strip() for p in existing.split(",")]
                             if existing else [])

            print(f"\n  ⏳ Analyzing required documents for {framework}...")
            analysis = generator.identify_required_policies(
                framework, existing_list
            )

            print(f"\n{'─'*60}")
            print(analysis)
            print(f"{'─'*60}")

            save_path = os.path.join(
                config.REPORT_DIR,
                f"policy_requirements_{timestamp()}.md"
            )
            with open(save_path, "w") as f:
                f.write(analysis)
            print(f"\n  ✅ Saved: {save_path}")

        elif choice == "4":
            # Full suite
            framework = select_framework()
            print(f"\n  Generating full policy suite for {framework}...")
            print("  This will generate multiple policies and may take several minutes.\n")

            relevant = [
                name for name, info in POLICY_CATALOG.items()
                if any(fw_part in framework
                       for fw_part in info.get("frameworks", []))
            ]
            if not relevant:
                relevant = list(POLICY_CATALOG.keys())[:5]

            print(f"  Will generate {len(relevant)} policies:")
            for i, p in enumerate(relevant, 1):
                print(f"    {i}. {p}")

            if not confirm(f"Proceed with generating {len(relevant)} policies?"):
                continue

            for i, pol_name in enumerate(relevant, 1):
                print(f"\n  [{i}/{len(relevant)}] ⏳ Generating: {pol_name}...")
                try:
                    content = generator.generate_policy(
                        pol_name, framework=framework
                    )
                    generator.save_document(content, "policy", pol_name)
                    print(f"  [{i}/{len(relevant)}] ✅ Done: {pol_name}")
                except Exception as e:
                    print(f"  [{i}/{len(relevant)}] ❌ Failed: {pol_name} — {e}")

            print(f"\n  ✅ Policy suite generation complete!")
            print(f"  📁 Saved to: {config.POLICY_DIR}/")

        elif choice == "5":
            break

        else:
            print("  ⚠️  Invalid option.")


# ══════════════════════════════════════════════════════
# 3. CONTROL MAPPING
# ══════════════════════════════════════════════════════

def run_control_mapping():
    """Run the control mapping workflow."""
    print("\n" + "=" * 60)
    print("  🔗 CONTROL MAPPING ENGINE")
    print("=" * 60)

    company = get_company_info()
    mapper = ControlMapper(company)

    print("\n  Options:")
    print("    1. Map between two frameworks")
    print("    2. Create unified control framework")

    choice = input("\n  Select option: ").strip()

    if choice == "1":
        print("\n  Select SOURCE framework:")
        source = select_framework()
        print("\n  Select TARGET framework:")
        target = select_framework()

        print(f"\n  ⏳ Mapping {source} → {target}...")
        mapping = mapper.map_frameworks(source, target)

        print(f"\n{'─'*60}")
        print(mapping)
        print(f"{'─'*60}")

        save_path = os.path.join(
            config.REPORT_DIR,
            f"control_mapping_{source.replace(' ','_')}_to_"
            f"{target.replace(' ','_')}_{timestamp()}.md"
        )
        with open(save_path, "w") as f:
            f.write(mapping)
        print(f"\n  ✅ Saved: {save_path}")

    elif choice == "2":
        frameworks = []
        print("  Enter frameworks (one per line, empty line to finish):")
        while True:
            fw = input("    Framework: ").strip()
            if not fw:
                break
            frameworks.append(fw)

        if len(frameworks) < 2:
            print("  ⚠️  Need at least 2 frameworks.")
            return

        print(f"\n  ⏳ Creating unified framework for: "
              f"{', '.join(frameworks)}...")
        unified = mapper.identify_unified_controls(frameworks)

        print(f"\n{'─'*60}")
        print(unified)
        print(f"{'─'*60}")

        save_path = os.path.join(
            config.REPORT_DIR,
            f"unified_framework_{timestamp()}.md"
        )
        with open(save_path, "w") as f:
            f.write(unified)
        print(f"\n  ✅ Saved: {save_path}")


# ══════════════════════════════════════════════════════
# 4. DOCUMENT REVIEW
# ══════════════════════════════════════════════════════

def run_document_review():
    """Review existing documents."""
    print("\n" + "=" * 60)
    print("  📄 DOCUMENT REVIEW ENGINE")
    print("=" * 60)

    company = get_company_info()
    reviewer = DocumentReviewer(company)

    print("\n  Options:")
    print("    1. Review document against a framework")
    print("    2. Quality assessment (no framework)")
    print("    3. Compare two documents")
    print("    4. Generate improved version")

    choice = input("\n  Select option: ").strip()

    if choice == "1":
        file_path = input("  Path to document: ").strip()
        if not os.path.exists(file_path):
            print(f"  ❌ File not found: {file_path}")
            return

        framework = select_framework()

        print(f"\n  ⏳ Reading document...")
        doc_text = reviewer.read_document(file_path)
        doc_name = os.path.basename(file_path)
        print(f"  📏 Document length: {len(doc_text):,} characters")

        print(f"\n  ⏳ Reviewing against {framework}...")
        review = reviewer.review_policy_against_framework(
            doc_text, doc_name, framework
        )

        # Display & save
        if isinstance(review, dict):
            output = json.dumps(review, indent=2)
        else:
            output = str(review)

        print(f"\n{'─'*60}")
        print(output[:3000])
        if len(output) > 3000:
            print("\n  ...[truncated]")
        print(f"{'─'*60}")

        reviewer.save_review(review, doc_name)

    elif choice == "2":
        file_path = input("  Path to document: ").strip()
        if not os.path.exists(file_path):
            print(f"  ❌ File not found: {file_path}")
            return

        print(f"\n  ⏳ Reading and assessing quality...")
        doc_text = reviewer.read_document(file_path)
        doc_name = os.path.basename(file_path)

        result = reviewer.review_policy_quality(doc_text, doc_name)

        print(f"\n{'─'*60}")
        print(result)
        print(f"{'─'*60}")

        reviewer.save_review(result, doc_name)

    elif choice == "3":
        path1 = input("  Path to Document 1: ").strip()
        path2 = input("  Path to Document 2: ").strip()

        if not os.path.exists(path1) or not os.path.exists(path2):
            print("  ❌ One or both files not found.")
            return

        print(f"\n  ⏳ Comparing documents...")
        text1 = reviewer.read_document(path1)
        text2 = reviewer.read_document(path2)

        result = reviewer.compare_policies(
            text1, os.path.basename(path1),
            text2, os.path.basename(path2)
        )

        print(f"\n{'─'*60}")
        print(result)
        print(f"{'─'*60}")

        save_path = os.path.join(
            config.REPORT_DIR,
            f"comparison_{timestamp()}.md"
        )
        with open(save_path, "w") as f:
            f.write(result)
        print(f"\n  ✅ Saved: {save_path}")

    elif choice == "4":
        file_path = input("  Path to original document: ").strip()
        if not os.path.exists(file_path):
            print(f"  ❌ File not found: {file_path}")
            return

        print("  Enter review findings / improvement notes:")
        print("  (Type your notes, then press Enter twice to finish)")
        lines = []
        while True:
            line = input("  > ")
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        findings = "\n".join(lines)

        print(f"\n  ⏳ Generating improved version...")
        doc_text = reviewer.read_document(file_path)
        doc_name = os.path.basename(file_path)

        result = reviewer.generate_improvement_draft(
            doc_text, doc_name, findings
        )

        print(f"\n{'─'*60}")
        print(result[:3000])
        if len(result) > 3000:
            print("\n  ...[truncated]")
        print(f"{'─'*60}")

        save_path = os.path.join(
            config.POLICY_DIR,
            f"improved_{doc_name.replace(' ','_')}_{timestamp()}.md"
        )
        with open(save_path, "w") as f:
            f.write(result)
        print(f"\n  ✅ Saved: {save_path}")


# ══════════════════════════════════════════════════════
# 5. EVIDENCE TRACKER
# ══════════════════════════════════════════════════════

def run_evidence_tracker():
    """Run evidence tracking workflow."""
    print("\n" + "=" * 60)
    print("  📁 EVIDENCE TRACKER")
    print("=" * 60)

    company = get_company_info()
    framework = select_framework()
    tracker = EvidenceTracker(company, framework)

    print("\n  Options:")
    print("    1. Generate evidence requirements")
    print("    2. Generate evidence request email")

    choice = input("\n  Select option: ").strip()

    if choice == "1":
        print(f"\n  ⏳ Generating evidence requirements for {framework}...")
        evidence = tracker.generate_evidence_requirements()

        if evidence:
            print(f"\n  ✅ Generated {len(evidence)} evidence items")

            # Show first few
            for ev in evidence[:5]:
                print(f"\n    📋 {ev.get('evidence_id', 'N/A')}: "
                      f"{ev.get('evidence_name', 'N/A')}")
                print(f"       Control: {ev.get('control_id', '')}")
                print(f"       Type: {ev.get('evidence_type', '')}")
                print(f"       Source: {ev.get('typical_source', '')}")

            if len(evidence) > 5:
                print(f"\n    ... and {len(evidence) - 5} more items")

            # Save
            tracker.save_tracker()

            # Export Excel
            if confirm("Export to Excel?"):
                xlsx_path = os.path.join(
                    config.REPORT_DIR,
                    f"evidence_tracker_{timestamp()}.xlsx"
                )
                export_evidence_tracker_xlsx(
                    evidence, company["name"], framework, xlsx_path
                )

    elif choice == "2":
        recipient = input("  Recipient role (e.g., IT Manager): ").strip()
        if not recipient:
            print("  ⚠️  No recipient specified.")
            return

        # Generate requirements first if not done
        print(f"\n  ⏳ Generating evidence list and email...")
        tracker.generate_evidence_requirements()
        email = tracker.generate_evidence_request_email(recipient)

        print(f"\n{'─'*60}")
        print(email)
        print(f"{'─'*60}")

        save_path = os.path.join(
            config.REPORT_DIR,
            f"evidence_request_email_{timestamp()}.md"
        )
        with open(save_path, "w") as f:
            f.write(email)
        print(f"\n  ✅ Saved: {save_path}")


# ══════════════════════════════════════════════════════
# 6. AUDIT READINESS
# ══════════════════════════════════════════════════════

def run_audit_readiness():
    """Run audit readiness assessment."""
    print("\n" + "=" * 60)
    print("  ✅ AUDIT READINESS ASSESSMENT")
    print("=" * 60)

    company = get_company_info()
    framework = select_framework()
    assessor = AuditReadinessAssessor(company, framework)

    print("\n  Options:")
    print("    1. Assess audit readiness")
    print("    2. Generate preparation plan")

    choice = input("\n  Select option: ").strip()

    if choice == "1":
        existing_pols = input("  List existing policies (comma-separated, or Enter): ").strip()
        policy_list = ([p.strip() for p in existing_pols.split(",")]
                       if existing_pols else None)

        print(f"\n  ⏳ Assessing audit readiness...")
        result = assessor.assess_readiness(policy_list=policy_list)

        print(f"\n{'─'*60}")
        print(result)
        print(f"{'─'*60}")

        save_path = os.path.join(
            config.REPORT_DIR,
            f"audit_readiness_{timestamp()}.md"
        )
        with open(save_path, "w") as f:
            f.write(result)
        print(f"\n  ✅ Saved: {save_path}")

    elif choice == "2":
        audit_date = input("  Planned audit date (YYYY-MM-DD): ").strip()
        if not audit_date:
            audit_date = "2025-06-01"

        print(f"\n  ⏳ Generating preparation plan for {audit_date}...")
        plan = assessor.generate_audit_preparation_plan(audit_date)

        print(f"\n{'─'*60}")
        print(plan)
        print(f"{'─'*60}")

        save_path = os.path.join(
            config.REPORT_DIR,
            f"audit_prep_plan_{timestamp()}.md"
        )
        with open(save_path, "w") as f:
            f.write(plan)
        print(f"\n  ✅ Saved: {save_path}")


# ══════════════════════════════════════════════════════
# 7. QUICK POLICY (Single Command)
# ══════════════════════════════════════════════════════

def quick_policy():
    """Generate a single policy quickly."""
    company = get_company_info()
    gen = PolicyGenerator(company)
    policy_name = input("\n  Policy name: ").strip()
    if not policy_name:
        print("  ⚠️  No policy name provided.")
        return

    print(f"\n  ⏳ Generating {policy_name}...")
    content = gen.generate_policy(policy_name)

    print(f"\n{'─'*60}")
    print(content[:3000])
    if len(content) > 3000:
        print("\n  ...[truncated — see full file]")
    print(f"{'─'*60}")

    gen.save_document(content, "policy", policy_name)


# ══════════════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════════════

def main():
    """Main application entry point."""
    # Check API key
    if (config.ANTHROPIC_API_KEY == "your-anthropic-api-key-here"
            and not os.getenv("ANTHROPIC_API_KEY")):
        print("\n  ⚠️  WARNING: No Anthropic API key configured!")
        print("  Set it via:")
        print("    export ANTHROPIC_API_KEY='your-key-here'")
        print("  Or edit config.py directly.\n")

    print("""
    ╔══════════════════════════════════════════════════╗
    ║         🛡️  GRC AUTOMATION TOOLKIT v1.0          ║
    ║                                                  ║
    ║   Powered by Anthropic Claude                    ║
    ║   Automate your GRC consulting workflows         ║
    ╚══════════════════════════════════════════════════╝
    """)

    while True:
        print("\n" + "─" * 55)
        print("  MAIN MENU")
        print("─" * 55)
        print("  1. 🔍 Gap Assessment")
        print("  2. 📋 Policy & Procedure Generator")
        print("  3. 🔗 Control Mapping")
        print("  4. 📄 Document Review")
        print("  5. 📁 Evidence Tracker")
        print("  6. ✅ Audit Readiness")
        print("  7. ⚡ Quick Policy (Single Command)")
        print("  8. 🌐 Launch Web UI")
        print("  9. 🚪 Exit")

        choice = input("\n  Select option: ").strip()

        if choice == "1":
            run_gap_assessment()
        elif choice == "2":
            run_policy_generator()
        elif choice == "3":
            run_control_mapping()
        elif choice == "4":
            run_document_review()
        elif choice == "5":
            run_evidence_tracker()
        elif choice == "6":
            run_audit_readiness()
        elif choice == "7":
            quick_policy()
        elif choice == "8":
            print("\n  🌐 Launching Streamlit Web UI...")
            print("  Run this command in your terminal:")
            print("    streamlit run web_app.py\n")
            try:
                os.system("streamlit run web_app.py")
            except Exception:
                print("  ⚠️  Could not auto-launch. "
                      "Run 'streamlit run web_app.py' manually.")
        elif choice == "9":
            print("\n  👋 Goodbye! Stay compliant!\n")
            sys.exit(0)
        else:
            print("  ⚠️  Invalid option. Please try again.")


if __name__ == "__main__":
    main()