# 🛡️ GRC Automation Toolkit

> **Automate your Governance, Risk, and Compliance (GRC) workflows with AI.**

A Python-based toolkit that helps GRC consultants and security professionals automate tedious manual tasks like gap assessments, policy creation, procedure development, risk register building, and audit preparation.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-412991.svg)

---

## 📋 Table of Contents

- [What Does This Tool Do?](#-what-does-this-tool-do)
- [Features](#-features)
- [Supported Frameworks](#-supported-frameworks)
- [Time Savings](#-time-savings)
- [Prerequisites](#-prerequisites)
- [Installation (Step-by-Step)](#-installation-step-by-step)
- [Getting Your OpenAI API Key](#-getting-your-openai-api-key)
- [How to Run the Tool](#-how-to-run-the-tool)
- [Using the Web Interface](#-using-the-web-interface-recommended)
- [Using the Command Line](#-using-the-command-line)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🤔 What Does This Tool Do?

If you're a GRC consultant or security professional, you know these tasks take forever:

- ❌ Manually assessing an organization against NIST CSF, ISO 27001, SOC 2, etc.
- ❌ Writing security policies from scratch for every client
- ❌ Creating step-by-step procedures for security operations
- ❌ Building risk registers from gap assessment findings
- ❌ Tracking evidence collection for audits
- ❌ Reviewing existing policies for compliance gaps

**This toolkit automates all of that using AI.** You describe a company's current security state, and the tool:

✅ Evaluates every control against your chosen framework  
✅ Assigns maturity scores and identifies gaps  
✅ Generates professional reports (Excel, Word, JSON)  
✅ Creates complete, ready-to-use security policies  
✅ Builds risk registers with treatment plans  
✅ Tracks evidence collection for audit prep  
✅ Reviews existing documents for compliance gaps  

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🔍 Gap Assessment Engine** | Assess organizations against compliance frameworks with AI-powered analysis |
| **📋 Policy Generator** | Generate complete, professional security policies in minutes |
| **📝 Procedure Generator** | Create detailed step-by-step operational procedures |
| **⚠️ Risk Register Builder** | Auto-generate risk registers from gap assessment findings |
| **📁 Evidence Tracker** | Track evidence collection status for audit preparation |
| **📄 Document Reviewer** | Upload and review existing policies against frameworks |
| **🔗 Control Mapper** | Map controls between different frameworks |
| **✅ Audit Readiness Scorer** | Assess overall readiness for upcoming audits |
| **📊 Excel Reports** | Color-coded, professionally formatted Excel exports |
| **📄 Word Reports** | Complete gap assessment reports in Word format |
| **🌐 Web Interface** | Easy-to-use browser-based interface (Streamlit) |
| **💻 Command Line** | Full CLI for power users |

---

## 📚 Supported Frameworks

- **NIST CSF 2.0** — Cybersecurity Framework
- **ISO 27001:2022** — Information Security Management
- **SOC 2 Type II** — Trust Services Criteria
- **HIPAA** — Healthcare Security Rule
- **PCI DSS 4.0** — Payment Card Industry
- **CMMC 2.0** — Cybersecurity Maturity Model
- **NIST 800-53 Rev 5** — Security Controls
- **CIS Controls v8** — Center for Internet Security
- **GDPR** — General Data Protection Regulation

---

## ⏱️ Time Savings

| Manual GRC Task | Traditional Time | With This Tool |
|----------------|-----------------|----------------|
| Gap Assessment (full framework) | 40–80 hours | 2–3 hours |
| Writing a Security Policy | 8–16 hours | 10 minutes |
| Creating a Procedure | 4–8 hours | 10 minutes |
| Building a Risk Register | 16–24 hours | 15 minutes |
| Cross-Framework Mapping | 20–40 hours | 20 minutes |
| Executive Summary | 4–8 hours | 2 minutes |
| Remediation Roadmap | 8–16 hours | 5 minutes |

---

## 📦 Prerequisites

Before you start, you need **three things** installed on your computer:

### 1. Python (version 3.9 or higher)

**Check if you already have Python:**
Open your Terminal (Mac/Linux) or Command Prompt (Windows) and type:

```bash
python --version
or
python3 --version
```
If you see something like `Python 3.9.x` or higher, you're good! If not:

- Windows: Download from python.org/downloads. During installation, CHECK THE BOX that says "Add Python to PATH".
- Mac: Download from python.org/downloads or use Homebrew: `brew install python`
- Linux: Run sudo apt install python3 python3-pip (Ubuntu/Debian) or sudo yum install python3 (CentOS/RHEL)

### 2. Git
Check if you already have Git:
```
git --version
```
If not installed:

- Windows: Download from git-scm.com
- Mac: Run `xcode-select --install` in Terminal, or download from git-scm.com
- Linux: Run `sudo apt install git`


### 3. An Anthropic API Key
You'll need an API key from Anthropic (makers of Claude AI). See the section below on how to get one.

🚀 Installation (Step-by-Step)
Follow these steps exactly — they work on Windows, Mac, and Linux.

Step 1: Open your Terminal / Command Prompt

- Windows: Press `Win + R`, type `cmd`, press Enter. (Or search for "Command Prompt" in the Start Menu)
- Mac: Press `Cmd + Space`, type "Terminal", press Enter.
- Linux: Press `Ctrl + Alt + T`

Step 2: Navigate to where you want the project
Choose a folder where you want to save the project. For example:
```bash
cd Desktop
```
Step 3: Clone (download) this repository
```bash
git clone https://github.com/H2oenter/grc-toolkit.git
```
Step 4: Go into the project folder
```bash
cd grc-toolkit
```
Step 5: Create a virtual environment (recommended)
This keeps the project's packages separate from your other Python projects.
On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
On Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
You should see (venv) appear at the beginning of your command line. This means the virtual environment is active.
Step 6: Install required packages
```bash
pip install -r requirements.txt
```
This will download and install all the necessary packages. It may take a minute or two.
Step 7: Set up your API key
You need to tell the tool your Anthropic API key. There are two ways:
Option A: Environment Variable (Recommended)
On Windows (Command Prompt):
```bash
set ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```
On Windows (PowerShell):
```bash
$env:ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```
On Mac/Linux:
```bash
export ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```
💡 Tip: To make this permanent so you don't have to type it every time:

- Mac/Linux: Add the `export` line to your `~/.bashrc` or `~/.zshrc` file
Windows: Search for "Environment Variables" in Settings and add it there


Option B: Create a .env file
```bash
cp .env.example .env
```
Then open `.env` in any text editor and replace the placeholder with your real key.

⚠️ WARNING: The `.env` file is excluded from Git by `.gitignore.` Never commit your API key to GitHub.

Step 8: Verify everything works
```bash
python quickstart.py
```
If you see a policy being generated and saved, everything is working! 🎉

🔑 Getting Your Anthropic API Key
---
1. Go to console.anthropic.com
2. Sign up or log in
3. Go to "API Keys" in the left sidebar (or visit console.anthropic.com/settings/keys)
4. Click "Create Key"
5. Give it a name like "GRC Toolkit"
6. Copy the key immediately — you won't be able to see it again!
7. The key looks like: `sk-ant-api03-abc123...xyz789`

💰 Cost: The tool uses Claude Sonnet 4 by default. A full gap assessment typically costs $2–8 in API calls. A single policy costs about $0.10–0.50. You can switch to claude-3-5-haiku-20241022 in config.py for cheaper/faster runs.
---
🖥️ How to Run the Tool
You have two options: a web browser interface or a command line interface.
🌐 Using the Web Interface (Recommended)
The web interface is the easiest way to use the tool. It runs in your browser.
```bash
streamlit run web_app.py
```
This will:

1. Start a local web server
2. Automatically open your browser to `http://localhost:8501`
3. Show you the GRC Automation Toolkit dashboard

If the browser doesn't open automatically, just open your browser and go to: `http://localhost:8501`
To stop the web server, go back to your terminal and press `Ctrl + C`

### Web Interface Walkthrough:

1. Fill in company info in the left sidebar (company name, industry, size)
2. Select a framework (e.g., NIST CSF 2.0)
3. Choose a tab at the top:
- 🔍 Gap Assessment — Run a full gap assessment
- 📋 Policy Generator — Create policies and procedures
- 📄 Document Review — Upload and review existing documents
- ⚠️ Risk Register — Build risk registers
- 📁 Evidence Tracker — Track audit evidence
- ✅ Audit Readiness — Assess audit readiness
4. Follow the prompts in each tab
5. Download results as Excel, Word, or JSON files

---

💻 Using the Command Line
If you prefer typing commands:
```bash
python main.py
```
This opens an interactive menu:
```
╔══════════════════════════════════════════════╗
║        GRC AUTOMATION TOOLKIT v1.0           ║
║                                              ║
║   Automate your GRC consulting workflows     ║
╚══════════════════════════════════════════════╝
```
  MAIN MENU
--------------------------------------------------
  1. 🔍 Gap Assessment
  2. 📋 Policy & Procedure Generator
  3. 🔗 Control Mapping
  4. ⚙️  Quick Policy (Single Command)
  5. 🚪 Exit

Just type the number of the option you want and press Enter.
---
🗂️ Project Structure
```
grc-toolkit/
│
├── README.md                  ← You are here
├── LICENSE                    ← MIT License
├── requirements.txt           ← Python package dependencies
├── .gitignore                 ← Files Git should ignore
├── .env.example               ← Example environment variables file
│
├── config.py                  ← Configuration (API key, model, paths)
├── main.py                    ← Command-line interface entry point
├── web_app.py                 ← Streamlit web interface
├── quickstart.py              ← Quick test script
│
├── engines/                   ← Core AI-powered engines
│   ├── __init__.py
│   ├── gap_assessment.py      ← Gap assessment logic
│   ├── policy_generator.py    ← Policy & procedure creation
│   ├── risk_register.py       ← Risk register builder
│   ├── document_reviewer.py   ← Existing document analysis
│   ├── evidence_tracker.py    ← Evidence collection tracking
│   ├── audit_readiness.py     ← Audit readiness scoring
│   └── control_mapper.py      ← Cross-framework control mapping
│
├── utils/                     ← Utility modules
│   ├── __init__.py
│   ├── ai_client.py           ← Anthropic Claude API wrapper
│   ├── document_exporter.py   ← Excel & Word export functions
│   └── framework_loader.py    ← Framework JSON file loader
│
├── frameworks/                ← Framework knowledge bases (JSON)
│   ├── nist_csf.json          ← NIST Cybersecurity Framework 2.0
│   ├── iso27001.json          ← ISO 27001:2022
│   ├── soc2.json              ← SOC 2 Type II Trust Services Criteria
│   └── hipaa.json             ← HIPAA Security Rule
│
└── outputs/                   ← Generated documents (auto-created)
    ├── gap_assessments/       ← Gap assessment results
    ├── policies/              ← Generated policies
    ├── procedures/            ← Generated procedures
    └── reports/               ← Executive summaries, roadmaps, etc.
```
---
❓ Troubleshooting
"python is not recognized as a command"

- Windows: Python wasn't added to PATH during installation. Reinstall Python and CHECK the "Add to PATH" box. Or try `py` instead of `python`.
- Mac/Linux: Try `python3` instead of `python`.

"pip is not recognized"

- Try `python -m pip install -r requirements.txt` instead.
- Or `python3 -m pip install -r requirements.txt`

"No module named 'anthropic'"

- Make sure you activated the virtual environment (Step 5).
- Run `pip install -r requirements.txt` again.

"API key error" or "Authentication failed"

- Double-check your API key is correct.
- Anthropic keys start with `sk-ant-` — make sure you copied the full key.
- Make sure you set it with the right command for your operating system (Step 7).
- Check that you have credits on your Anthropic account at console.anthropic.com/settings/billing.

"Rate limit exceeded"

- You're making too many API calls too quickly.
- Wait a minute and try again.
- Consider switching to `claude-3-5-haiku-20241022` in `config.py` which has higher rate limits.

The web app won't start

- Make sure Streamlit is installed: `pip install streamlit`
- Try: `python -m streamlit run web_app.py`
- Check that no other app is using port 8501.

"Framework file not found"

- The tool will fall back to AI-generated framework knowledge.
- To fix: make sure you're running from the project root folder (grc-toolkit/).

Excel/Word export not working

- Run: `pip install python-docx openpyxl`
- These are already in requirements.txt, so `pip install -r requirements.txt` should cover it.

My virtual environment won't activate (Windows)

Try running PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again: `venv\Scripts\activate`
---

🔒 Security Notes
- Never commit your API key to GitHub. Use environment variables or a `.env` file instead.
- The `.gitignore` file is set up to exclude sensitive files.
- All generated documents are saved locally in the `outputs/` folder.
- No data is sent anywhere except to Anthropic's API for processing.
- Review generated policies before adopting them — AI output should always be reviewed by a qualified professional.
---

🛠️ Configuration Options
You can customize the tool by editing config.py:
```python
# Switch to a cheaper/faster model
MODEL = "claude-3-5-haiku-20241022"   # Cheaper, faster, good for testing
MODEL = "claude-sonnet-4-20250514"             # Best quality, recommended for production

# Change output directories
OUTPUT_DIR = "my_custom_output_folder"
```
🤝 Contributing
Contributions are welcome! Here's how:
1. Fork this repository
2. Create a feature branch: `git checkout -b feature/my-new-feature`
3. Make your changes
4. Test everything works: `python quickstart.py`
5. Commit: `git commit -m "Add my new feature"`
6. Push: `git push origin feature/my-new-feature`
7. Open a Pull Request

**Ideas for Contributions:**
- Add more framework JSON files (PCI DSS, CMMC, CIS Controls, etc.)
- Add more export formats (PDF, HTML)
- Build additional assessment templates
- Improve the web UI
- Add database storage for historical assessments
- Add multi-language support for policies
- Create industry-specific policy templates

---
📄 License

This project is licensed under the MIT License — see the LICENSE file for details.
---
🙏 Acknowledgments
- Built with Anthropic Claude AI
- Web interface powered by Streamlit
- Excel exports via openpyxl
- Word exports via python-docx
---

📧 Questions?

Open an issue on this repository or reach out to me.

⭐ If you find this tool useful, please give it a star on GitHub!




