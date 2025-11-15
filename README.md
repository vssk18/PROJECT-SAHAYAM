# 🛡️ Project SAHAYAM

![Python](https://img.shields.io/badge/Language-Python-blue.svg)
![C++](https://img.shields.io/badge/Language-C++-blue.svg)
![Java](https://img.shields.io/badge/Language-Java-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Last Commit](https://img.shields.io/github/last-commit/vssk18/PROJECT-SAHAYAM)

> Practical cyber safety clinics for seniors and families, with offline tools and actionable checklists.  
> *Weekly park sessions & campus seminars – Since Aug 2024*

---

## ⚡ Problem Statement

Many older adults in our community use Android phones for WhatsApp and banking, but lack essential protections: no screen lock, no MFA, outdated OS, and high exposure to KYC/UPI/refund scams.  
**SAHAYAM** focuses on simple, high-impact digital safety habits and core security settings that can be achieved in one clinic visit and sustained in the weeks after.

---

## 🏗️ Repository Structure

```plaintext
PROJECT-SAHAYAM/
├── apps/                     # Offline-friendly security tools (C++, Java, Python)
│   ├── cpp_sms_filter/       # C++ SMS scam filter
│   ├── java_passphrase_trainer/  # Java passphrase trainer
│   ├── py_checklist_generator/   # One-page checklist generator
│   ├── py_clinic_assistant/      # Main clinic flow + reports
│   ├── py_metrics_logger/        # Summarise anonymized metrics CSV
│   ├── py_phishing_sms/          # Fake KYC / UPI / refund SMS generator
│   ├── py_qr_demo/               # Safe vs fake UPI QR demo
│   ├── py_password_checker/      # Password pattern strength explainer
│   ├── py_pdf_reports/           # Markdown → PDF helper (Pandoc)
│   └── py_dashboard/             # Simple CLI menu for clinics
├── materials/                # One-page checklists & reports (Markdown)
│   ├── templates/            # Base templates for checklists/reports
│   └── generated/            # Per-participant checklists & reports (git-ignored)
├── metrics/                  # Anonymized before/after CSVs
│   └── baseline_vs_week1.csv # Example synthetic dataset (300 rows)
├── docs/                     # Seminar slides & short methods + findings report
├── ops/                      # Session plan, consent note, follow-up script
├── .github/                  # Issue templates and community health files
├── Makefile                  # Quick demo & helper targets
├── README.md
└── LICENSE
```

---

## 🛠️ Security-Focused Tools (apps/)

- **cpp_sms_filter/**  
  Offline C++ SMS scam detector for KYC / UPI / OTP / refund / prize patterns, with simple severity scoring.

- **java_passphrase_trainer/**  
  Console passphrase trainer to walk users through building longer passphrases and explains why reuse is risky.

- **py_checklist_generator/**  
  Generates a one-page, personalized checklist (English/Teleugu/Hindi) for each participant with concrete next steps.

- **py_clinic_assistant/**  
  Main clinic flow: asks risk questions, computes before/after risk score, logs metrics, updates checklist,  
  and writes a plain-language report in `materials/generated/`.

- **py_metrics_logger/**  
  Reads anonymized CSVs in `metrics/` to print summary stats on MFA adoption, screen lock, and scam quiz improvements.

- **py_phishing_sms/**  
  Generates realistic but fake SMS messages in categories like bank KYC, UPI refunds, courier fees, electricity cut-off, and job/prize offers for scam-spotting exercises.

- **py_qr_demo/**  
  Builds two QR codes (safe shop payment vs. fake refund/“KYC update”) to show why name and amount must always be checked on the UPI payment screen.

- **py_password_checker/**  
  Does **not** ask for real passwords; estimates strength by pattern type and length and explains “very weak”, “ok”, “good” categories.

- **py_pdf_reports/**  
  Uses Pandoc (if installed) to convert Markdown clinic reports into PDFs for printing.

- **py_dashboard/**  
  A small CLI menu to:
  1. Run a new clinic session  
  2. Show current metrics summary  
  3. List available security reports  
  4. Exit

---

## 🚀 Quick Demo

From a fresh clone (with `g++`, `javac`, and Python 3 installed), run:

```bash
# Activate the virtual environment if needed
source .venv/bin/activate

# Run the demo (requires Makefile quick-demo target to be present)
make quick-demo
```

This will:
1. Build the C++ SMS scam filter and scan a sample SMS file.
2. Run the Java passphrase trainer with demo input.
3. Generate a sample checklist with the Python tool.

---

### Example: Running the Clinic Assistant

```bash
cd apps/py_dashboard
python dashboard.py

# Choose:
# 1) Run a new clinic session
# 2) Show current metrics summary
```

---

## 📊 Metrics & Privacy

For each session/month, we track anonymized counts:
- MFA enabled on Google / WhatsApp (before → after)
- Screen lock set
- Bank daily limit set/updated
- Scam-SMS identification score (before vs. after)
- 1-week retention of changes

**No raw passwords, OTPs, or bank details are ever recorded.**

---

## ⚙️ Environment & Installation

To run the SAHAYAM tools on your own machine:

```bash
cd ~/Projects/project-sahayam

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required Python packages
pip install --upgrade pip
pip install qrcode pillow
```

*Make sure g++ and javac are available on your system for compiling C++ and Java tools.*

---

## 🛡️ Security & Conduct

- For vulnerability reports, see [`SECURITY.md`](./SECURITY.md).
- Please follow our guidelines in [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).

---

## 🛠️ Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

To report bugs or request features:
- 🐞 [Bug Report](https://github.com/vssk18/PROJECT-SAHAYAM/issues/new?template=bug_report.md)
- 🌟 [Feature Request](https://github.com/vssk18/PROJECT-SAHAYAM/issues/new?template=feature_request.md)

---

## 📄 License

This project is licensed under MIT. See the [LICENSE](./LICENSE) file for details.

---

## 👨‍💻 Maintainer

**Varanasi Sai Srinivasa Karthik**  
B.Tech CSE (Cybersecurity), GITAM University, Hyderabad  
- 📧 varanasikarthik44@gmail.com
- 📧 svaranas3@gitam.in
- 📧 vsskarthik@gmail.com
- [GitHub Profile](https://github.com/vssk18)

---

## 🙌 Acknowledgements

Special thanks to all contributors, seniors, trainers, and volunteers supporting digital safety through SAHAYAM.