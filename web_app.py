"""
GRC Automation Toolkit — Streamlit Web UI
==========================================
Location: grc_toolkit/web_app.py
Run with: streamlit run web_app.py

This provides a browser-based interface for all GRC automation features:
- Gap Assessments
- Policy & Procedure Generation
- Document Review
- Risk Register
- Evidence Tracking
- Audit Readiness
"""

import streamlit as st
import json
import os
import io
import pandas as pd
from datetime import datetime, timedelta

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    
# Import engines
from engines.gap_assessment import GapAssessment
from engines.policy_generator import PolicyGenerator, POLICY_CATALOG
from engines.risk_register import RiskRegister
from engines.document_reviewer import DocumentReviewer
from engines.evidence_tracker import EvidenceTracker
from engines.audit_readiness import AuditReadinessAssessor
from engines.control_mapper import ControlMapper
from utils.framework_loader import load_framework, get_all_controls
from utils.document_exporter import (
    export_gap_assessment_xlsx,
    export_risk_register_xlsx,
    export_evidence_tracker_xlsx,
    export_gap_assessment_docx,
    export_policy_docx,
)
import config

# Create output directories
for d in ["outputs/gap_assessments", "outputs/policies",
          "outputs/procedures", "outputs/reports"]:
    os.makedirs(d, exist_ok=True)


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="GRC Automation Toolkit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F4E79;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER: FRAMEWORK CATEGORIES FOR GUIDED INPUT
# ============================================================
def get_framework_categories(framework: str) -> dict:
    """Return major assessment domains for a given framework."""
    catalog = {
        "NIST CSF 2.0": {
            "GV": "Govern — Organizational Context, Risk Strategy, Oversight, Cybersecurity Supply Chain",
            "ID": "Identify — Asset Management, Risk Assessment, Improvement",
            "PR": "Protect — Identity Mgmt & Access Control, Awareness & Training, Data Security, Platform Security, Technology Infrastructure Resilience",
            "DE": "Detect — Continuous Monitoring, Adverse Event Analysis",
            "RS": "Respond — Incident Management, Incident Analysis, Incident Response Reporting & Communication, Incident Mitigation",
            "RC": "Recover — Incident Recovery Plan Execution, Incident Recovery Communication",
        },
        "ISO 27001:2022": {
            "A.5": "Organizational Controls — Policies, Roles, Segregation, Threat Intel, Asset Mgmt, Access, Supplier Relations, Incident Mgmt, BCM, Compliance",
            "A.6": "People Controls — Screening, Employment Terms, Awareness & Training, Disciplinary, Termination, Remote Working",
            "A.7": "Physical Controls — Perimeters, Entry Controls, Securing Offices, Monitoring, Protection Against Threats, Equipment Security",
            "A.8": "Technological Controls — User Endpoints, Privileged Access, Access Restriction, Authentication, Malware, Vulnerabilities, Config, Backup, Logging, Network, Crypto, SDLC",
        },
        "SOC 2 Type II": {
            "CC1": "Control Environment — Integrity & Ethics, Board Oversight, Structure & Authority, Competence, Accountability",
            "CC2": "Communication & Information — Quality Information, Internal Communication, External Communication",
            "CC3": "Risk Assessment — Objectives, Risk Analysis, Fraud Risk, Significant Change",
            "CC4": "Monitoring Activities — Ongoing Evaluations, Deficiency Communication",
            "CC5": "Control Activities — Control Selection, Technology Controls, Policy Deployment",
            "CC6": "Logical & Physical Access — Access Security, Registration, Role-Based Access, Boundary Protection, Transmission, Malicious Software",
            "CC7": "System Operations — Vulnerability Detection, Anomaly Monitoring, Security Event Evaluation, Incident Response, Recovery",
            "CC8": "Change Management — Authorization, Design, Development, Configuration, Testing, Approval, Implementation",
            "CC9": "Risk Mitigation — Business Disruption, Vendor & Business Partner Risk",
        },
        "HIPAA": {
            "ADMIN": "Administrative Safeguards — Security Management, Assigned Responsibility, Workforce Security, Information Access, Training, Incidents, Contingency, Evaluation, BAAs",
            "PHYS": "Physical Safeguards — Facility Access, Workstation Use & Security, Device & Media Controls",
            "TECH": "Technical Safeguards — Access Control, Audit Controls, Integrity, Person Authentication, Transmission Security",
        },
        "PCI DSS 4.0": {
            "R1": "Requirement 1 — Install and Maintain Network Security Controls",
            "R2": "Requirement 2 — Apply Secure Configurations to All System Components",
            "R3": "Requirement 3 — Protect Stored Account Data",
            "R4": "Requirement 4 — Protect Cardholder Data with Strong Cryptography During Transmission",
            "R5": "Requirement 5 — Protect All Systems and Networks from Malicious Software",
            "R6": "Requirement 6 — Develop and Maintain Secure Systems and Software",
            "R7": "Requirement 7 — Restrict Access to System Components and Cardholder Data by Business Need to Know",
            "R8": "Requirement 8 — Identify Users and Authenticate Access to System Components",
            "R9": "Requirement 9 — Restrict Physical Access to Cardholder Data",
            "R10": "Requirement 10 — Log and Monitor All Access to System Components and Cardholder Data",
            "R11": "Requirement 11 — Test Security of Systems and Networks Regularly",
            "R12": "Requirement 12 — Support Information Security with Organizational Policies and Programs",
        },
        "CMMC 2.0": {
            "AC": "Access Control",
            "AT": "Awareness & Training",
            "AU": "Audit & Accountability",
            "CM": "Configuration Management",
            "IA": "Identification & Authentication",
            "IR": "Incident Response",
            "MA": "Maintenance",
            "MP": "Media Protection",
            "PE": "Physical Protection",
            "PS": "Personnel Security",
            "RA": "Risk Assessment",
            "CA": "Security Assessment",
            "SC": "System & Communications Protection",
            "SI": "System & Information Integrity",
        },
    }
    # Fallback for any unlisted framework
    return catalog.get(framework, {
        "GOV": "Governance — Policies, Roles, Risk Management Strategy",
        "PROTECT": "Protection — Access Control, Data Security, Training, Platform Security",
        "DETECT": "Detection — Monitoring, Logging, Alerting, Anomaly Detection",
        "RESPOND": "Response — Incident Management, Communication, Mitigation",
        "RECOVER": "Recovery — Business Continuity, Disaster Recovery, Lessons Learned",
    })


# ============================================================
# HELPER: DISPLAY GAP ASSESSMENT RESULTS
# ============================================================
def display_gap_results(results: list, assessment_obj=None):
    """Render gap assessment results with metrics, charts, table, and export."""
    if not results:
        st.warning("No results to display.")
        return

    st.divider()
    st.subheader("📊 Assessment Results")

    # --- Statistics ---
    total = len(results)
    assessed = [r for r in results if r.get("score")]
    avg_score = sum(r["score"] for r in assessed) / len(assessed) if assessed else 0

    maturity_counts = {}
    priority_counts = {}
    for r in results:
        m = r.get("maturity", "Not Assessed")
        p = r.get("priority", "N/A")
        maturity_counts[m] = maturity_counts.get(m, 0) + 1
        priority_counts[p] = priority_counts.get(p, 0) + 1

    # --- Top Metrics ---
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Controls", total)
    m2.metric("Avg Maturity", f"{avg_score:.1f} / 5.0")
    m3.metric("Fully Implemented",
              maturity_counts.get("Fully Implemented", 0))
    m4.metric("Not Implemented",
              maturity_counts.get("Not Implemented", 0))
    m5.metric("Critical Findings",
              priority_counts.get("Critical", 0))

    # --- Charts ---
    if HAS_PLOTLY:
        chart1, chart2 = st.columns(2)

        with chart1:
            mat_df = pd.DataFrame(
                [{"Maturity": k, "Count": v} for k, v in maturity_counts.items()]
            )
            color_map = {
                "Fully Implemented": "#27AE60",
                "Largely Implemented": "#2ECC71",
                "Partially Implemented": "#F39C12",
                "Minimally Implemented": "#E67E22",
                "Not Implemented": "#E74C3C",
                "Not Assessed": "#95A5A6",
            }
            fig1 = px.pie(mat_df, values="Count", names="Maturity",
                          title="Maturity Distribution",
                          color="Maturity", color_discrete_map=color_map)
            fig1.update_traces(textposition="inside",
                               textinfo="value+percent")
            fig1.update_layout(height=420, margin=dict(t=40, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with chart2:
            func_scores = {}
            for r in results:
                fn = r.get("function", "Unknown")
                if fn not in func_scores:
                    func_scores[fn] = []
                if r.get("score"):
                    func_scores[fn].append(r["score"])

            func_df = pd.DataFrame([
                {"Function": fn,
                 "Avg Score": round(sum(s)/len(s), 1) if s else 0}
                for fn, s in func_scores.items()
            ])
            if not func_df.empty:
                fig2 = px.bar(func_df, x="Function", y="Avg Score",
                              title="Average Score by Domain",
                              color="Avg Score",
                              color_continuous_scale=["#E74C3C",
                                                      "#F39C12",
                                                      "#27AE60"],
                              range_color=[1, 5])
                fig2.add_hline(y=3, line_dash="dash", line_color="gray",
                               annotation_text="Target Baseline (3.0)")
                fig2.update_layout(height=420, margin=dict(t=40, b=20))
                st.plotly_chart(fig2, use_container_width=True)

    # --- Filterable Data Table ---
    st.subheader("📋 Detailed Findings")

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sel_mat = st.multiselect("Filter by Maturity",
                                  list(maturity_counts.keys()),
                                  default=list(maturity_counts.keys()),
                                  key="tbl_mat")
    with fc2:
        sel_pri = st.multiselect("Filter by Priority",
                                  list(priority_counts.keys()),
                                  default=list(priority_counts.keys()),
                                  key="tbl_pri")
    with fc3:
        all_funcs = list(set(r.get("function", "Unknown") for r in results))
        sel_func = st.multiselect("Filter by Function",
                                   all_funcs, default=all_funcs,
                                   key="tbl_func")

    filtered = [
        r for r in results
        if r.get("maturity", "Not Assessed") in sel_mat
        and r.get("priority", "N/A") in sel_pri
        and r.get("function", "Unknown") in sel_func
    ]

    if filtered:
        df = pd.DataFrame(filtered)
        show_cols = [c for c in [
            "control_id", "function", "category", "maturity", "score",
            "gap", "recommendations", "priority", "estimated_effort"
        ] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, height=500)
    else:
        st.info("No results match current filters.")

    # --- Export Buttons ---
    st.subheader("📥 Export Options")
    ex1, ex2, ex3, ex4 = st.columns(4)

    with ex1:
        if st.button("📊 Export Excel", key="exp_xlsx"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(config.GAP_ASSESSMENT_DIR,
                                f"gap_assessment_{ts}.xlsx")
            meta = {
                "company": st.session_state.get("company", {}),
                "framework": st.session_state.get("framework_select", ""),
                "timestamp": datetime.now().isoformat(),
            }
            export_gap_assessment_xlsx(results, meta, path)
            with open(path, "rb") as fh:
                st.download_button("⬇️ Download Excel", fh.read(),
                                   file_name=os.path.basename(path),
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   key="dl_xlsx")

    with ex2:
        json_str = json.dumps({
            "metadata": {
                "company": st.session_state.get("company", {}),
                "framework": st.session_state.get("framework_select", ""),
                "timestamp": datetime.now().isoformat(),
            },
            "results": results
        }, indent=2)
        st.download_button("📄 Download JSON", json_str,
                           file_name=f"gap_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                           mime="application/json",
                           key="dl_json")

    with ex3:
        if st.button("📝 Executive Summary", key="btn_exec_sum"):
            if assessment_obj:
                with st.spinner("Generating executive summary..."):
                    summary = assessment_obj.generate_executive_summary()
                    st.session_state.exec_summary = summary

    with ex4:
        if st.button("🗺️ Remediation Roadmap", key="btn_roadmap"):
            if assessment_obj:
                with st.spinner("Generating roadmap..."):
                    roadmap = assessment_obj.get_remediation_roadmap()
                    st.session_state.remediation_roadmap = roadmap

    # Show generated executive summary
    if "exec_summary" in st.session_state:
        with st.expander("📝 Executive Summary", expanded=True):
            st.markdown(st.session_state.exec_summary)
            st.download_button("⬇️ Download Summary",
                               st.session_state.exec_summary,
                               file_name="executive_summary.md",
                               mime="text/markdown", key="dl_exec")

    # Show generated roadmap
    if "remediation_roadmap" in st.session_state:
        with st.expander("🗺️ Remediation Roadmap", expanded=True):
            st.markdown(st.session_state.remediation_roadmap)
            st.download_button("⬇️ Download Roadmap",
                               st.session_state.remediation_roadmap,
                               file_name="remediation_roadmap.md",
                               mime="text/markdown", key="dl_road")


# ============================================================
# SIDEBAR — always visible
# ============================================================
def render_sidebar() -> tuple:
    """Render sidebar and return (company dict, framework string)."""
    st.sidebar.header("🏢 Company Information")

    if "company" not in st.session_state:
        st.session_state.company = {
            "name": "", "industry": "Technology",
            "size": "51-200 employees", "description": ""
        }

    name = st.sidebar.text_input("Company Name",
                                  value=st.session_state.company["name"],
                                  key="sb_name")
    industry = st.sidebar.selectbox(
        "Industry",
        ["Technology", "Healthcare", "Financial Services",
         "Manufacturing", "Retail", "Government", "Education",
         "Energy", "Legal", "Consulting", "Insurance",
         "Non-Profit", "Other"],
        key="sb_ind"
    )
    size = st.sidebar.selectbox(
        "Company Size",
        ["1-50 employees", "51-200 employees", "201-500 employees",
         "501-1000 employees", "1001-5000 employees", "5000+ employees"],
        key="sb_size"
    )
    desc = st.sidebar.text_area("Brief Description", height=80,
                                 key="sb_desc",
                                 placeholder="What does the company do?")

    company = {"name": name, "industry": industry,
               "size": size, "description": desc}
    st.session_state.company = company

    st.sidebar.divider()
    st.sidebar.header("📋 Framework")
    framework = st.sidebar.selectbox("Select Framework",
                                      config.SUPPORTED_FRAMEWORKS,
                                      key="framework_select")

    st.sidebar.divider()
    st.sidebar.caption("GRC Toolkit v1.0")
    st.sidebar.caption(f"AI Model: {config.MODEL}")

    return company, framework


# ============================================================
# TAB 1 — GAP ASSESSMENT
# ============================================================
def render_tab_gap_assessment(company: dict, framework: str):
    st.header("🔍 Gap Assessment Engine")
    st.write(f"Assess **{company['name']}** against **{framework}**")

    method = st.radio(
        "Assessment Input Method",
        ["📝 Category-by-Category (Guided)", "📋 Bulk Text Input"],
        horizontal=True, key="gap_method"
    )

    # --- GUIDED ---
    if "Category-by-Category" in method:
        st.subheader(f"Describe your current state for each {framework} domain")
        st.caption("The more detail you provide, the better the assessment. "
                   "Type 'none' if nothing exists for a domain.")

        categories = get_framework_categories(framework)
        current_states = {}

        for cat_id, cat_name in categories.items():
            with st.expander(f"📁 {cat_id} — {cat_name}", expanded=False):
                current_states[cat_id] = st.text_area(
                    f"Current state for {cat_id}",
                    height=130, key=f"guided_{cat_id}",
                    placeholder=(
                        f"What tools, processes, policies exist for {cat_name}?\n"
                        f"• Tools (e.g., Okta, CrowdStrike, Splunk)\n"
                        f"• Processes (e.g., quarterly access reviews)\n"
                        f"• Policies (e.g., documented and approved)\n"
                        f"• Gaps you already know about"
                    ),
                    label_visibility="collapsed",
                )

        if st.button("🚀 Run Gap Assessment", type="primary",
                     key="run_guided"):
            filled = {k: v for k, v in current_states.items() if v.strip()}
            if not filled:
                st.error("Please describe at least one domain before running.")
                return

            progress = st.progress(0, text="Initializing...")
            status = st.empty()

            try:
                assessment = GapAssessment(company, framework)

                # Load framework controls grouped by category
                fw_data = load_framework(framework)
                controls = get_all_controls(fw_data)
                cat_controls = {}
                for ctrl in controls:
                    ck = ctrl["category_id"]
                    if ck not in cat_controls:
                        cat_controls[ck] = {
                            "function": ctrl["function"],
                            "function_id": ctrl["function_id"],
                            "category": ctrl["category"],
                            "category_id": ctrl["category_id"],
                            "controls": [],
                        }
                    cat_controls[ck]["controls"].append(ctrl)

                all_results = []
                total = len(filled)
                for idx, (cat_id, state_text) in enumerate(filled.items()):
                    status.text(f"Assessing {cat_id}...")
                    progress.progress((idx) / total,
                                       text=f"Assessing {cat_id} "
                                            f"({idx+1}/{total})...")

                    if cat_id in cat_controls:
                        res = assessment._evaluate_category(
                            cat_controls[cat_id], state_text
                        )
                        all_results.extend(res)
                    else:
                        # If no matching controls in JSON, use AI knowledge
                        dummy_cat = {
                            "function": cat_id,
                            "function_id": cat_id,
                            "category": categories[cat_id],
                            "category_id": cat_id,
                            "controls": [{
                                "control_id": f"{cat_id}-GEN",
                                "description": categories[cat_id],
                            }],
                        }
                        res = assessment._evaluate_category(
                            dummy_cat, state_text
                        )
                        all_results.extend(res)

                progress.progress(1.0, text="✅ Assessment complete!")
                status.empty()

                assessment.results = all_results
                st.session_state.gap_results = all_results
                st.session_state.gap_assessment = assessment

                st.success(f"✅ Done! {len(all_results)} controls evaluated.")
                display_gap_results(all_results, assessment)

            except Exception as e:
                st.error(f"❌ Assessment failed: {e}")
                st.exception(e)

    # --- BULK ---
    elif "Bulk" in method:
        st.subheader("Describe Your Entire Security Posture")
        bulk = st.text_area(
            "Comprehensive description",
            height=300, key="bulk_text",
            placeholder=(
                "Describe your full security program:\n\n"
                "• Identity & Access: Okta SSO, MFA enforced, quarterly reviews...\n"
                "• Network: Palo Alto firewalls, segmented VLANs...\n"
                "• Endpoints: CrowdStrike EDR on all laptops, auto-patch...\n"
                "• Data: AES-256 at rest, TLS 1.2+ in transit, DLP...\n"
                "• Monitoring: Splunk SIEM, 24/7 SOC...\n"
                "• Incident Response: Documented IR plan, tested annually...\n"
                "• Governance: ISO 27001 certified, annual risk assessment...\n"
                "• Physical: Badge access, cameras, visitor logs...\n"
                "• Vendors: Annual vendor risk assessments...\n"
                "• BCP/DR: Documented, tested semi-annually..."
            ),
        )

        if st.button("🚀 Run Bulk Assessment", type="primary",
                     key="run_bulk"):
            if not bulk.strip():
                st.error("Please provide a description first.")
                return

            with st.spinner("Analyzing your security posture against "
                            f"{framework}... This may take a few minutes."):
                try:
                    assessment = GapAssessment(company, framework)
                    cats = get_framework_categories(framework)
                    state_map = {cat_id: bulk for cat_id in cats}
                    results = assessment.run_bulk_assessment(state_map)

                    st.session_state.gap_results = results
                    st.session_state.gap_assessment = assessment

                    st.success(f"✅ {len(results)} controls evaluated.")
                    display_gap_results(results, assessment)

                except Exception as e:
                    st.error(f"❌ Assessment failed: {e}")
                    st.exception(e)

    # Show previous results if they exist
    if ("gap_results" in st.session_state
            and "gap_assessment" in st.session_state
            and not st.session_state.get("_just_ran")):
        st.divider()
        st.subheader("📂 Previous Assessment Results")
        display_gap_results(st.session_state.gap_results,
                            st.session_state.gap_assessment)


# ============================================================
# TAB 2 — POLICY & PROCEDURE GENERATOR
# ============================================================
def render_tab_policy_generator(company: dict, framework: str):
    st.header("📋 Policy & Procedure Generator")

    sub_tab = st.radio(
        "What would you like to generate?",
        ["📄 Single Policy", "📑 Single Procedure",
         "📚 Full Policy Suite", "🔎 Required Policy Analysis"],
        horizontal=True, key="pol_mode"
    )

    gen = PolicyGenerator(company)

    # ---- SINGLE POLICY ----
    if "Single Policy" in sub_tab:
        st.subheader("Generate a Policy Document")

        col_a, col_b = st.columns([2, 1])

        with col_a:
            policy_type = st.selectbox(
                "Policy Type",
                list(POLICY_CATALOG.keys()) + ["✏️ Custom Policy"],
                key="pol_type"
            )
            if "Custom" in policy_type:
                policy_type = st.text_input("Enter custom policy name:",
                                             key="custom_pol_name")

        with col_b:
            align_fw = st.selectbox(
                "Align with Framework",
                ["Auto-detect"] + config.SUPPORTED_FRAMEWORKS,
                key="pol_fw"
            )

        context = st.text_area(
            "Additional Context (optional)",
            height=100, key="pol_ctx",
            placeholder="e.g., We use AWS and Azure, have 200 remote workers, "
                        "handle PHI data, use GitHub for source code..."
        )

        custom_reqs = st.text_area(
            "Custom Requirements (optional)",
            height=80, key="pol_reqs",
            placeholder="e.g., Must include data residency requirements for EU, "
                        "must reference our existing ISMS..."
        )

        if st.button("📝 Generate Policy", type="primary", key="gen_pol"):
            if not policy_type:
                st.error("Please select or enter a policy type.")
                return
            fw = framework if align_fw == "Auto-detect" else align_fw
            with st.spinner(f"Generating {policy_type}..."):
                try:
                    content = gen.generate_policy(
                        policy_type,
                        framework=fw,
                        additional_context=context,
                        custom_requirements=custom_reqs,
                    )
                    st.session_state.gen_policy = content
                    st.session_state.gen_policy_name = policy_type
                except Exception as e:
                    st.error(f"Generation failed: {e}")

        if "gen_policy" in st.session_state:
            st.divider()
            st.subheader(f"Generated: {st.session_state.gen_policy_name}")
            st.markdown(st.session_state.gen_policy)

            dc1, dc2 = st.columns(2)
            with dc1:
                st.download_button(
                    "📥 Download as Markdown (.md)",
                    st.session_state.gen_policy,
                    file_name=f"{st.session_state.gen_policy_name.replace(' ','_')}.md",
                    mime="text/markdown", key="dl_pol_md"
                )
            with dc2:
                if st.button("📥 Export as Word (.docx)", key="exp_pol_docx"):
                    path = os.path.join(
                        config.POLICY_DIR,
                        f"{st.session_state.gen_policy_name.replace(' ','_')}.docx"
                    )
                    export_policy_docx(
                        st.session_state.gen_policy,
                        st.session_state.gen_policy_name,
                        company["name"], path
                    )
                    with open(path, "rb") as fh:
                        st.download_button(
                            "⬇️ Download Word File", fh.read(),
                            file_name=os.path.basename(path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="dl_pol_docx"
                        )

    # ---- SINGLE PROCEDURE ----
    elif "Single Procedure" in sub_tab:
        st.subheader("Generate a Procedure Document")

        proc_name = st.text_input(
            "Procedure Name", key="proc_name",
            placeholder="e.g., Incident Response Procedure, "
                        "User Access Review Procedure, Vulnerability Management..."
        )
        related_pol = st.text_input(
            "Related Policy (optional)", key="proc_rel",
            placeholder="e.g., Incident Response Policy"
        )
        proc_ctx = st.text_area(
            "Additional Context (optional)", height=100, key="proc_ctx",
            placeholder="Specific tools, team structure, escalation contacts..."
        )

        if st.button("📝 Generate Procedure", type="primary",
                     key="gen_proc"):
            if not proc_name:
                st.error("Please enter a procedure name.")
                return
            with st.spinner(f"Generating: {proc_name}..."):
                try:
                    content = gen.generate_procedure(
                        proc_name,
                        related_policy=related_pol,
                        additional_context=proc_ctx,
                    )
                    st.session_state.gen_procedure = content
                    st.session_state.gen_procedure_name = proc_name
                except Exception as e:
                    st.error(f"Generation failed: {e}")

        if "gen_procedure" in st.session_state:
            st.divider()
            st.subheader(f"Generated: {st.session_state.gen_procedure_name}")
            st.markdown(st.session_state.gen_procedure)
            st.download_button(
                "📥 Download Procedure (.md)",
                st.session_state.gen_procedure,
                file_name=f"{st.session_state.gen_procedure_name.replace(' ','_')}_procedure.md",
                mime="text/markdown", key="dl_proc"
            )

    # ---- FULL SUITE ----
    elif "Full Policy Suite" in sub_tab:
        st.subheader(f"Generate Full Policy Suite for {framework}")
        st.write("This will generate all relevant policies for the selected "
                 "framework. It may take several minutes.")

        relevant = [
            name for name, info in POLICY_CATALOG.items()
            if any(fw_part in framework
                   for fw_part in info.get("frameworks", []))
        ]
        if not relevant:
            relevant = list(POLICY_CATALOG.keys())

        st.write(f"**{len(relevant)} policies** will be generated:")
        for i, p in enumerate(relevant, 1):
            st.write(f"  {i}. {p}")

        if st.button(f"🚀 Generate All {len(relevant)} Policies",
                     type="primary", key="gen_suite"):
            progress = st.progress(0)
            generated_policies = {}

            for idx, pol_name in enumerate(relevant):
                progress.progress(
                    idx / len(relevant),
                    text=f"Generating {pol_name} ({idx+1}/{len(relevant)})..."
                )
                try:
                    content = gen.generate_policy(pol_name,
                                                   framework=framework)
                    generated_policies[pol_name] = content
                    gen.save_document(content, "policy", pol_name)
                except Exception as e:
                    generated_policies[pol_name] = f"ERROR: {e}"

            progress.progress(1.0, text="✅ All policies generated!")
            st.session_state.policy_suite = generated_policies
            st.success(f"✅ {len(generated_policies)} policies generated! "
                       f"Saved to {config.POLICY_DIR}/")

        if "policy_suite" in st.session_state:
            st.divider()
            for name, content in st.session_state.policy_suite.items():
                with st.expander(f"📄 {name}"):
                    if content.startswith("ERROR"):
                        st.error(content)
                    else:
                        st.markdown(content[:3000] + "\n\n*[truncated for preview]*"
                                    if len(content) > 3000 else content)
                        st.download_button(
                            f"📥 Download {name}",
                            content,
                            file_name=f"{name.replace(' ','_')}.md",
                            mime="text/markdown",
                            key=f"dl_suite_{name}"
                        )

    # ---- REQUIRED POLICY ANALYSIS ----
    elif "Required Policy" in sub_tab:
        st.subheader(f"Policy Requirements Analysis for {framework}")

        existing = st.text_area(
            "List your existing policies (one per line, or leave blank)",
            height=120, key="existing_pols",
            placeholder="Information Security Policy\nAccess Control Policy\n..."
        )
        existing_list = [p.strip() for p in existing.split("\n")
                         if p.strip()] if existing else []

        if st.button("🔎 Analyze Requirements", type="primary",
                     key="analyze_pols"):
            with st.spinner("Analyzing policy requirements..."):
                try:
                    analysis = gen.identify_required_policies(
                        framework, existing_list
                    )
                    st.session_state.policy_analysis = analysis
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

        if "policy_analysis" in st.session_state:
            st.divider()
            st.markdown(st.session_state.policy_analysis)
            st.download_button(
                "📥 Download Analysis",
                st.session_state.policy_analysis,
                file_name="policy_requirements_analysis.md",
                mime="text/markdown", key="dl_pol_analysis"
            )
            # ============================================================
# TAB 3 — DOCUMENT REVIEW
# ============================================================
def render_tab_document_review(company: dict, framework: str):
    st.header("📄 Document Review Engine")
    st.write("Upload existing policies or procedures for AI-powered analysis.")

    review_mode = st.radio(
        "Review Mode",
        ["🔍 Framework Compliance Review",
         "✅ Quality Assessment",
         "⚖️ Compare Two Documents",
         "✨ Generate Improved Version"],
        horizontal=True, key="review_mode"
    )

    reviewer = DocumentReviewer(company)

    # --- Helper: read uploaded file ---
    def read_upload(uploaded) -> str:
        """Read content from an uploaded file."""
        if uploaded is None:
            return ""
        fname = uploaded.name.lower()
        if fname.endswith(".txt") or fname.endswith(".md"):
            return uploaded.read().decode("utf-8", errors="ignore")
        elif fname.endswith(".docx"):
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            try:
                text = reviewer.read_document(tmp_path)
            finally:
                os.unlink(tmp_path)
            return text
        elif fname.endswith(".pdf"):
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            try:
                text = reviewer.read_document(tmp_path)
            finally:
                os.unlink(tmp_path)
            return text
        else:
            return uploaded.read().decode("utf-8", errors="ignore")

    # ---- FRAMEWORK COMPLIANCE REVIEW ----
    if "Framework Compliance" in review_mode:
        st.subheader(f"Review Document Against {framework}")

        uploaded = st.file_uploader(
            "Upload document to review",
            type=["txt", "md", "docx", "pdf"],
            key="review_upload_fw"
        )

        if uploaded:
            doc_text = read_upload(uploaded)
            if doc_text:
                with st.expander("📄 Document Preview", expanded=False):
                    st.text_area("Content Preview",
                                 doc_text[:5000] + ("\n\n...[truncated]"
                                 if len(doc_text) > 5000 else ""),
                                 height=250, disabled=True,
                                 key="fw_preview")

                st.info(f"📏 Document length: {len(doc_text):,} characters")

                if st.button("🔍 Review Against Framework", type="primary",
                             key="run_fw_review"):
                    with st.spinner(f"Reviewing {uploaded.name} against "
                                    f"{framework}..."):
                        try:
                            review = reviewer.review_policy_against_framework(
                                doc_text, uploaded.name, framework
                            )
                            st.session_state.fw_review = review
                            st.session_state.fw_review_doc = uploaded.name
                        except Exception as e:
                            st.error(f"Review failed: {e}")
                            st.exception(e)

        if "fw_review" in st.session_state:
            st.divider()
            st.subheader(f"Review Results: {st.session_state.fw_review_doc}")

            review_data = st.session_state.fw_review

            if isinstance(review_data, dict) and review_data.get("format") != "text":
                # Structured JSON response
                # Quality score
                quality = review_data.get("document_quality_assessment",
                                           review_data.get("quality_assessment", {}))
                if isinstance(quality, dict):
                    score = quality.get("overall_quality_score",
                                        quality.get("score", "N/A"))
                    q1, q2, q3 = st.columns(3)
                    q1.metric("Overall Quality Score", f"{score}/10")
                    q2.metric("Framework", review_data.get("framework", ""))
                    q3.metric("Review Date",
                              review_data.get("review_date", "")[:10])

                # Findings
                findings = review_data.get("specific_findings",
                                            review_data.get("findings", []))
                if findings and isinstance(findings, list):
                    st.subheader("🔎 Specific Findings")
                    for f in findings:
                        sev = f.get("severity", "Info")
                        icon = {"Critical": "🔴", "High": "🟠",
                                "Medium": "🟡", "Low": "🟢",
                                "Informational": "ℹ️"}.get(sev, "⬜")
                        with st.expander(
                            f"{icon} [{sev}] "
                            f"{f.get('finding_id', '')}: "
                            f"{f.get('section', f.get('area', 'General'))}",
                            expanded=(sev in ["Critical", "High"])
                        ):
                            st.write(f"**Issue:** {f.get('description', '')}")
                            st.write(f"**Recommendation:** "
                                     f"{f.get('recommendation', '')}")
                            ref = f.get("reference", f.get("framework_reference", ""))
                            if ref:
                                st.write(f"**Framework Reference:** {ref}")

                # Gaps
                gaps = review_data.get("content_gaps",
                                        review_data.get("gaps", []))
                if gaps:
                    st.subheader("🕳️ Content Gaps")
                    if isinstance(gaps, list):
                        for g in gaps:
                            if isinstance(g, dict):
                                st.write(f"- **{g.get('topic', 'Gap')}**: "
                                         f"{g.get('description', str(g))}")
                            else:
                                st.write(f"- {g}")
                    elif isinstance(gaps, dict):
                        for k, v in gaps.items():
                            st.write(f"- **{k}**: {v}")

                # Positive observations
                positives = review_data.get("positive_observations",
                                             review_data.get("strengths", []))
                if positives:
                    st.subheader("✅ Positive Observations")
                    if isinstance(positives, list):
                        for p in positives:
                            st.write(f"- {p if isinstance(p, str) else p.get('observation', str(p))}")

                # Recommended actions
                actions = review_data.get("recommended_actions",
                                           review_data.get("recommendations", []))
                if actions:
                    st.subheader("📋 Recommended Actions")
                    if isinstance(actions, list):
                        for idx, a in enumerate(actions, 1):
                            if isinstance(a, dict):
                                st.write(f"{idx}. **{a.get('action', a.get('title', ''))}** "
                                         f"— {a.get('description', a.get('detail', ''))}")
                            else:
                                st.write(f"{idx}. {a}")

                # Download full review
                st.download_button(
                    "📥 Download Full Review (JSON)",
                    json.dumps(review_data, indent=2),
                    file_name=f"review_{st.session_state.fw_review_doc}.json",
                    mime="application/json", key="dl_fw_review"
                )

            else:
                # Plain text fallback
                content = (review_data.get("review", str(review_data))
                           if isinstance(review_data, dict)
                           else str(review_data))
                st.markdown(content)
                st.download_button(
                    "📥 Download Review",
                    content,
                    file_name=f"review_{st.session_state.fw_review_doc}.md",
                    mime="text/markdown", key="dl_fw_review_md"
                )

    # ---- QUALITY ASSESSMENT ----
    elif "Quality Assessment" in review_mode:
        st.subheader("Policy Quality Assessment")
        st.write("Review a policy against best-practice quality standards "
                 "(no specific framework required).")

        uploaded = st.file_uploader(
            "Upload policy document",
            type=["txt", "md", "docx", "pdf"],
            key="review_upload_qa"
        )

        if uploaded:
            doc_text = read_upload(uploaded)
            if doc_text:
                with st.expander("📄 Document Preview", expanded=False):
                    st.text_area("Preview", doc_text[:5000], height=200,
                                 disabled=True, key="qa_preview")

                if st.button("✅ Run Quality Assessment", type="primary",
                             key="run_qa"):
                    with st.spinner("Assessing document quality..."):
                        try:
                            result = reviewer.review_policy_quality(
                                doc_text, uploaded.name
                            )
                            st.session_state.qa_result = result
                        except Exception as e:
                            st.error(f"Assessment failed: {e}")

        if "qa_result" in st.session_state:
            st.divider()
            st.markdown(st.session_state.qa_result)
            st.download_button(
                "📥 Download Quality Assessment",
                st.session_state.qa_result,
                file_name="quality_assessment.md",
                mime="text/markdown", key="dl_qa"
            )

    # ---- COMPARE DOCUMENTS ----
    elif "Compare" in review_mode:
        st.subheader("Compare Two Documents")

        c1, c2 = st.columns(2)
        with c1:
            up1 = st.file_uploader("Upload Document 1",
                                    type=["txt", "md", "docx", "pdf"],
                                    key="cmp_up1")
        with c2:
            up2 = st.file_uploader("Upload Document 2",
                                    type=["txt", "md", "docx", "pdf"],
                                    key="cmp_up2")

        if up1 and up2:
            text1 = read_upload(up1)
            text2 = read_upload(up2)

            if st.button("⚖️ Compare Documents", type="primary",
                         key="run_cmp"):
                with st.spinner("Comparing documents..."):
                    try:
                        result = reviewer.compare_policies(
                            text1, up1.name, text2, up2.name
                        )
                        st.session_state.cmp_result = result
                    except Exception as e:
                        st.error(f"Comparison failed: {e}")

        if "cmp_result" in st.session_state:
            st.divider()
            st.markdown(st.session_state.cmp_result)
            st.download_button(
                "📥 Download Comparison",
                st.session_state.cmp_result,
                file_name="document_comparison.md",
                mime="text/markdown", key="dl_cmp"
            )

    # ---- GENERATE IMPROVED VERSION ----
    elif "Improved" in review_mode:
        st.subheader("Generate Improved Version of a Document")
        st.write("Upload an existing document and paste review findings — "
                 "the AI will generate an improved version.")

        uploaded = st.file_uploader(
            "Upload original document",
            type=["txt", "md", "docx", "pdf"],
            key="improve_upload"
        )

        findings_text = st.text_area(
            "Paste review findings / improvement notes",
            height=200, key="improve_findings",
            placeholder=("Paste the findings from a review, or describe "
                         "what you want improved:\n"
                         "- Add proper document control section\n"
                         "- Make policy statements auditable\n"
                         "- Add encryption requirements\n"
                         "- Align with ISO 27001 A.8.24...")
        )

        if uploaded and findings_text.strip():
            doc_text = read_upload(uploaded)
            if st.button("✨ Generate Improved Version", type="primary",
                         key="run_improve"):
                with st.spinner("Generating improved document..."):
                    try:
                        result = reviewer.generate_improvement_draft(
                            doc_text, uploaded.name, findings_text
                        )
                        st.session_state.improved_doc = result
                        st.session_state.improved_doc_name = uploaded.name
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

        if "improved_doc" in st.session_state:
            st.divider()
            st.subheader(f"Improved: {st.session_state.improved_doc_name}")
            st.markdown(st.session_state.improved_doc)
            st.download_button(
                "📥 Download Improved Document",
                st.session_state.improved_doc,
                file_name=f"improved_{st.session_state.improved_doc_name}.md",
                mime="text/markdown", key="dl_improved"
            )


# ============================================================
# TAB 4 — RISK REGISTER
# ============================================================
def render_tab_risk_register(company: dict, framework: str):
    st.header("⚠️ Risk Register Builder")

    source = st.radio(
        "Build risk register from:",
        ["📊 Gap Assessment Results",
         "📝 Manual Risk Description",
         "📁 Upload Existing Risk Data"],
        horizontal=True, key="risk_source"
    )

    risk_engine = RiskRegister(company)

    # ---- FROM GAP ASSESSMENT ----
    if "Gap Assessment" in source:
        if "gap_results" in st.session_state:
            results = st.session_state.gap_results
            critical = [r for r in results
                        if r.get("score") and r["score"] <= 2]
            high = [r for r in results
                    if r.get("score") and r["score"] == 3]

            st.info(f"📊 Found **{len(results)}** assessed controls | "
                    f"**{len(critical)}** critical gaps | "
                    f"**{len(high)}** partial gaps")

            if st.button("⚠️ Generate Risk Register", type="primary",
                         key="gen_risk_gap"):
                with st.spinner("Analyzing gaps and generating risks..."):
                    try:
                        risks = risk_engine.generate_from_gap_assessment(results)
                        st.session_state.risk_register = risks
                        st.session_state.risk_engine = risk_engine
                    except Exception as e:
                        st.error(f"Risk generation failed: {e}")
                        st.exception(e)
        else:
            st.warning("⚠️ No gap assessment results found. "
                       "Run a Gap Assessment first (Tab 1), then come back here.")

    # ---- MANUAL DESCRIPTION ----
    elif "Manual" in source:
        risk_desc = st.text_area(
            "Describe your organization's key risk areas",
            height=250, key="manual_risk",
            placeholder=(
                "Describe known risks, concerns, and threat landscape:\n\n"
                "• We handle sensitive customer PII but lack DLP controls\n"
                "• Our DR plan hasn't been tested in 2 years\n"
                "• Several employees use personal devices without MDM\n"
                "• Third-party vendor recently had a data breach\n"
                "• No formal vulnerability management program\n"
                "• Legacy systems running end-of-life software..."
            ),
        )

        if st.button("⚠️ Generate Risk Register", type="primary",
                     key="gen_risk_manual"):
            if not risk_desc.strip():
                st.error("Please describe your risk areas.")
                return
            with st.spinner("Generating risk register..."):
                try:
                    # Convert description into pseudo gap results
                    from utils.ai_client import structured_output
                    system_prompt = f"""You are a risk analyst. Convert the following risk 
description into gap assessment format for risk register generation.
For each risk area, create an entry with:
- control_id, function, category, maturity, score (1-5), gap, 
  recommendations, priority, current_state_assessment

Company: {company['name']} ({company['industry']})
Framework: {framework}
Return as a JSON array."""

                    pseudo_gaps = structured_output(
                        system_prompt,
                        f"Risk areas:\n{risk_desc}"
                    )
                    if isinstance(pseudo_gaps, dict):
                        pseudo_gaps = pseudo_gaps.get("gaps",
                                     pseudo_gaps.get("results", [pseudo_gaps]))

                    risks = risk_engine.generate_from_gap_assessment(pseudo_gaps)
                    st.session_state.risk_register = risks
                    st.session_state.risk_engine = risk_engine
                except Exception as e:
                    st.error(f"Failed: {e}")
                    st.exception(e)

    # ---- DISPLAY RISK REGISTER ----
    if "risk_register" in st.session_state:
        risks = st.session_state.risk_register
        st.divider()
        st.subheader(f"📋 Risk Register — {len(risks)} Risks Identified")

        if not risks:
            st.info("No risks generated.")
            return

        # Summary metrics
        r1, r2, r3, r4 = st.columns(4)
        levels = {}
        for r in risks:
            lvl = r.get("inherent_risk_level", "Unknown")
            levels[lvl] = levels.get(lvl, 0) + 1

        r1.metric("Total Risks", len(risks))
        r2.metric("🔴 Critical", levels.get("Critical", 0))
        r3.metric("🟠 High", levels.get("High", 0))
        r4.metric("🟡 Medium", levels.get("Medium", 0))

        # Risk heat map
        if HAS_PLOTLY:
            st.subheader("🗺️ Risk Heat Map")
            heat_data = []
            for r in risks:
                heat_data.append({
                    "Likelihood": r.get("likelihood", 3),
                    "Impact": r.get("impact", 3),
                    "Risk": r.get("risk_title",
                                  r.get("risk_id", "Unknown")),
                    "Level": r.get("inherent_risk_level", "Medium"),
                })
            heat_df = pd.DataFrame(heat_data)

            if not heat_df.empty:
                color_map = {"Critical": "#E74C3C", "High": "#E67E22",
                             "Medium": "#F39C12", "Low": "#27AE60"}
                fig = px.scatter(
                    heat_df, x="Likelihood", y="Impact",
                    color="Level", hover_name="Risk",
                    color_discrete_map=color_map,
                    title="Risk Heat Map (Inherent Risk)",
                    size_max=15,
                )
                fig.update_layout(
                    xaxis=dict(range=[0.5, 5.5],
                               title="Likelihood (1=Rare, 5=Almost Certain)"),
                    yaxis=dict(range=[0.5, 5.5],
                               title="Impact (1=Negligible, 5=Catastrophic)"),
                    height=450,
                )
                # Add quadrant shading
                fig.add_shape(type="rect", x0=3.5, y0=3.5, x1=5.5, y1=5.5,
                              fillcolor="rgba(231,76,60,0.1)", line_width=0)
                fig.add_shape(type="rect", x0=0.5, y0=0.5, x1=2.5, y1=2.5,
                              fillcolor="rgba(39,174,96,0.1)", line_width=0)
                st.plotly_chart(fig, use_container_width=True)

        # Risk table
        st.subheader("📋 Risk Details")
        for r in risks:
            lvl = r.get("inherent_risk_level", "Medium")
            icon = {"Critical": "🔴", "High": "🟠",
                    "Medium": "🟡", "Low": "🟢"}.get(lvl, "⬜")

            with st.expander(
                f"{icon} {r.get('risk_id', 'N/A')} — "
                f"{r.get('risk_title', 'Untitled')} "
                f"[{lvl} — Score: {r.get('inherent_risk_score', 'N/A')}]",
                expanded=(lvl in ["Critical"])
            ):
                tc1, tc2 = st.columns(2)
                with tc1:
                    st.write(f"**Category:** {r.get('risk_category', '')}")
                    st.write(f"**Threat Source:** {r.get('threat_source', '')}")
                    st.write(f"**Vulnerability:** {r.get('vulnerability', '')}")
                    st.write(f"**Likelihood:** {r.get('likelihood', '')}/5")
                    st.write(f"**Impact:** {r.get('impact', '')}/5")
                    st.write(f"**Inherent Risk:** {r.get('inherent_risk_score', '')} "
                             f"({lvl})")
                with tc2:
                    st.write(f"**Existing Controls:** "
                             f"{r.get('existing_controls', 'None')}")
                    st.write(f"**Residual Risk:** "
                             f"{r.get('residual_risk_score', '')} "
                             f"({r.get('residual_risk_level', '')})")
                    st.write(f"**Treatment:** {r.get('risk_treatment', '')}")
                    st.write(f"**Risk Owner:** {r.get('risk_owner', '')}")
                    st.write(f"**Target Date:** {r.get('target_date', '')}")

                st.write(f"**Description:** {r.get('risk_description', '')}")
                st.write(f"**Treatment Plan:** {r.get('treatment_plan', '')}")

                related = r.get("related_control_ids", [])
                if related:
                    st.write(f"**Related Controls:** {', '.join(related)}")

        # Export
        st.divider()
        st.subheader("📥 Export Risk Register")
        ex1, ex2, ex3 = st.columns(3)

        with ex1:
            st.download_button(
                "📄 Download JSON",
                json.dumps({"risks": risks}, indent=2),
                file_name=f"risk_register_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json", key="dl_risk_json"
            )

        with ex2:
            if st.button("📊 Export Excel", key="exp_risk_xlsx"):
                path = os.path.join(
                    config.REPORT_DIR,
                    f"risk_register_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )
                export_risk_register_xlsx(risks, company["name"], path)
                with open(path, "rb") as fh:
                    st.download_button(
                        "⬇️ Download Excel", fh.read(),
                        file_name=os.path.basename(path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_risk_xlsx"
                    )

        with ex3:
            if st.button("📝 Generate Treatment Plans", key="gen_treatment"):
                with st.spinner("Generating detailed treatment plans..."):
                    engine = st.session_state.get("risk_engine", risk_engine)
                    engine.risks = risks
                    plans = engine.generate_risk_treatment_plans()
                    st.session_state.treatment_plans = plans

        if "treatment_plans" in st.session_state:
            with st.expander("📝 Risk Treatment Plans", expanded=True):
                st.markdown(st.session_state.treatment_plans)
                st.download_button(
                    "📥 Download Treatment Plans",
                    st.session_state.treatment_plans,
                    file_name="risk_treatment_plans.md",
                    mime="text/markdown", key="dl_treatment"
                )


# ============================================================
# TAB 5 — EVIDENCE TRACKER
# ============================================================
def render_tab_evidence_tracker(company: dict, framework: str):
    st.header("📁 Evidence Tracker")
    st.write(f"Track evidence collection for **{framework}** audit preparation.")

    tracker = EvidenceTracker(company, framework)

    ev_mode = st.radio(
        "Mode",
        ["📋 Generate Evidence Requirements",
         "📧 Generate Evidence Request Email",
         "📂 Load Existing Tracker"],
        horizontal=True, key="ev_mode"
    )

    # ---- GENERATE REQUIREMENTS ----
    if "Generate Evidence" in ev_mode:
        st.subheader(f"Generate Evidence Requirements for {framework}")

        use_gap = False
        if "gap_results" in st.session_state:
            use_gap = st.checkbox(
                "Use gap assessment results to focus evidence requirements",
                value=True, key="ev_use_gap"
            )

        if st.button("📋 Generate Evidence List", type="primary",
                     key="gen_evidence"):
            with st.spinner("Generating evidence requirements..."):
                try:
                    controls = None
                    if use_gap and "gap_results" in st.session_state:
                        controls = st.session_state.gap_results

                    evidence = tracker.generate_evidence_requirements(controls)
                    st.session_state.evidence_items = evidence
                    st.session_state.evidence_tracker = tracker
                except Exception as e:
                    st.error(f"Failed: {e}")
                    st.exception(e)

    # ---- DISPLAY EVIDENCE LIST ----
    if "evidence_items" in st.session_state:
        evidence = st.session_state.evidence_items
        st.divider()
        st.subheader(f"📋 Evidence Requirements — {len(evidence)} Items")

        # Status summary
        status_counts = {}
        for e in evidence:
            s = e.get("status", "Not Collected")
            status_counts[s] = status_counts.get(s, 0) + 1

        collected = sum(v for k, v in status_counts.items()
                        if k in ["Collected", "Reviewed", "Approved"])
        total = len(evidence)
        pct = round(collected / total * 100, 1) if total > 0 else 0

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Total Evidence Items", total)
        p2.metric("Collected", collected)
        p3.metric("Outstanding", total - collected)
        p4.metric("Completion", f"{pct}%")

        # Progress bar
        st.progress(pct / 100,
                     text=f"Evidence collection: {pct}% complete")

        # Evidence table
        if evidence:
            ev_df = pd.DataFrame(evidence)
            show_cols = [c for c in [
                "evidence_id", "control_id", "evidence_name",
                "evidence_type", "description", "typical_source",
                "frequency", "priority", "status"
            ] if c in ev_df.columns]

            # Filter
            fil_status = st.multiselect(
                "Filter by Status",
                list(status_counts.keys()),
                default=list(status_counts.keys()),
                key="ev_filter_status"
            )
            filtered_ev = ev_df[ev_df["status"].isin(fil_status)]

            st.dataframe(filtered_ev[show_cols],
                         use_container_width=True, height=500)

        # Export
        st.subheader("📥 Export")
        ex1, ex2 = st.columns(2)
        with ex1:
            st.download_button(
                "📄 Download JSON",
                json.dumps({"evidence_items": evidence}, indent=2),
                file_name=f"evidence_tracker_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json", key="dl_ev_json"
            )
        with ex2:
            if st.button("📊 Export Excel", key="exp_ev_xlsx"):
                path = os.path.join(
                    config.REPORT_DIR,
                    f"evidence_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )
                export_evidence_tracker_xlsx(evidence, company["name"],
                                             framework, path)
                with open(path, "rb") as fh:
                    st.download_button(
                        "⬇️ Download Excel", fh.read(),
                        file_name=os.path.basename(path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_ev_xlsx"
                    )

    # ---- EMAIL GENERATOR ----
    if "Evidence Request Email" in ev_mode:
        st.subheader("Generate Evidence Request Email")

        recipient = st.text_input(
            "Recipient Role",
            placeholder="e.g., IT Manager, CISO, HR Director, DevOps Lead",
            key="ev_email_role"
        )

        if st.button("📧 Generate Email", type="primary",
                     key="gen_ev_email"):
            if not recipient:
                st.error("Please specify a recipient role.")
                return
            trk = st.session_state.get("evidence_tracker", tracker)
            if not trk.evidence_items and "evidence_items" in st.session_state:
                trk.evidence_items = st.session_state.evidence_items

            with st.spinner("Generating email..."):
                try:
                    email = trk.generate_evidence_request_email(recipient)
                    st.session_state.ev_email = email
                except Exception as e:
                    st.error(f"Failed: {e}")

        if "ev_email" in st.session_state:
            st.divider()
            st.subheader("📧 Evidence Request Email")
            st.markdown(st.session_state.ev_email)
            st.download_button(
                "📥 Download Email",
                st.session_state.ev_email,
                file_name="evidence_request_email.md",
                mime="text/markdown", key="dl_ev_email"
            )


# ============================================================
# TAB 6 — AUDIT READINESS
# ============================================================
def render_tab_audit_readiness(company: dict, framework: str):
    st.header("✅ Audit Readiness Assessment")
    st.write(f"Evaluate readiness for a **{framework}** audit.")

    assessor = AuditReadinessAssessor(company, framework)

    ar_mode = st.radio(
        "Action",
        ["📊 Assess Readiness", "📅 Generate Preparation Plan"],
        horizontal=True, key="ar_mode"
    )

    if "Assess Readiness" in ar_mode:
        st.subheader("Audit Readiness Assessment")

        # Gather available data
        has_gap = "gap_results" in st.session_state
        has_evidence = "evidence_items" in st.session_state
        has_risk = "risk_register" in st.session_state

        st.write("**Available data for assessment:**")
        st.write(f"  {'✅' if has_gap else '❌'} Gap Assessment Results")
        st.write(f"  {'✅' if has_evidence else '❌'} Evidence Tracker")
        st.write(f"  {'✅' if has_risk else '❌'} Risk Register")

        existing_pols = st.text_area(
            "List any existing policies (optional, one per line)",
            height=100, key="ar_pols",
            placeholder="Information Security Policy\nAccess Control Policy\n..."
        )
        policy_list = [p.strip() for p in existing_pols.split("\n")
                       if p.strip()] if existing_pols else None

        if st.button("✅ Assess Readiness", type="primary",
                     key="run_ar"):
            with st.spinner("Assessing audit readiness..."):
                try:
                    gap_data = st.session_state.get("gap_results")
                    ev_summary = None
                    if has_evidence:
                        trk = st.session_state.get("evidence_tracker")
                        if trk:
                            ev_summary = trk.get_collection_summary()

                    result = assessor.assess_readiness(
                        gap_results=gap_data,
                        evidence_summary=ev_summary,
                        policy_list=policy_list,
                    )
                    st.session_state.ar_result = result
                except Exception as e:
                    st.error(f"Assessment failed: {e}")
                    st.exception(e)

        if "ar_result" in st.session_state:
            st.divider()
            st.markdown(st.session_state.ar_result)
            st.download_button(
                "📥 Download Readiness Report",
                st.session_state.ar_result,
                file_name=f"audit_readiness_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown", key="dl_ar"
            )

    elif "Preparation Plan" in ar_mode:
        st.subheader("Audit Preparation Plan")

        audit_date = st.date_input(
            "Planned Audit Date",
            value=datetime.now() + timedelta(days=90),
            key="ar_date"
        )

        if st.button("📅 Generate Preparation Plan", type="primary",
                     key="gen_prep"):
            with st.spinner("Generating preparation plan..."):
                try:
                    gap_data = st.session_state.get("gap_results")
                    plan = assessor.generate_audit_preparation_plan(
                        audit_date.isoformat(),
                        gap_results=gap_data,
                    )
                    st.session_state.prep_plan = plan
                except Exception as e:
                    st.error(f"Failed: {e}")

        if "prep_plan" in st.session_state:
            st.divider()
            st.markdown(st.session_state.prep_plan)
            st.download_button(
                "📥 Download Preparation Plan",
                st.session_state.prep_plan,
                file_name=f"audit_prep_plan_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown", key="dl_prep"
            )


# ============================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================
def main():
    st.markdown(
        '<div class="main-header">🛡️ GRC Automation Toolkit</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">'
        'Automate Gap Assessments · Generate Policies & Procedures · '
        'Build Risk Registers · Track Evidence · Prepare for Audits'
        '</div>',
        unsafe_allow_html=True
    )

    # Sidebar
    company, framework = render_sidebar()

    # Validate company info
    if not company["name"]:
        st.info("👈 **Get started:** Enter your company information in the "
                "sidebar, then explore the tabs below.")
        st.stop()

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Gap Assessment",
        "📋 Policy Generator",
        "📄 Document Review",
        "⚠️ Risk Register",
        "📁 Evidence Tracker",
        "✅ Audit Readiness",
    ])

    with tab1:
        render_tab_gap_assessment(company, framework)

    with tab2:
        render_tab_policy_generator(company, framework)

    with tab3:
        render_tab_document_review(company, framework)

    with tab4:
        render_tab_risk_register(company, framework)

    with tab5:
        render_tab_evidence_tracker(company, framework)

    with tab6:
        render_tab_audit_readiness(company, framework)


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    main()