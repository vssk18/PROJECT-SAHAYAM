# Project SAHAYAM

Subtitle: Practical cyber safety clinics for seniors and families, with small offline tools and checklists.  
Timeline: Aug 2024 – Present • Weekly park sessions + campus seminars

## 1. Problem

Many older adults in my community use Android phones for WhatsApp and banking but lack basic protections: no screen lock, no MFA, outdated OS, and high exposure to KYC/UPI/refund scams.

SAHAYAM focuses on basic, high-impact security changes that can be made in 1 visit and sustained a week later.

## 2. Repository Layout

- materials/ – one-page checklists (EN/TE/HI) for take-home.
- apps/ – small, offline-friendly security tools in Bash, C, C++, Java, and Python.
- ops/ – session plan, consent note, and follow-up script.
- metrics/ – anonymized before/after CSVs and plots.
- docs/ – seminar slides and short report.
- Makefile – quick demo target for seminars.

## 3. Security-Focused Tools (apps/)

- cpp_sms_filter/ – offline SMS scam detector (KYC/UPI/OTP/link bait) with severity scoring.
- java_passphrase_trainer/ – console passphrase trainer that explains reuse and password managers.
- py_checklist_generator/ – personalized one-page plan in EN/TE/HI for each participant.
- py_link_analyzer/ – URL risk analyzer for suspicious TLDs, shorteners, and fake-support domains.
- bash_wifi_audit/ – Linux Wi-Fi audit for OPEN/WEAK networks (demo of public Wi-Fi risk).
- c_usb_guardian/ – Linux USB monitor that flags unknown devices (no random USB drives).

## 4. Quick Demo

From a fresh clone (with g++, javac, and python3 installed), run:

make quick-demo

This will:
1) Build the C++ SMS scam filter and scan a sample SMS file.  
2) Run the Java passphrase trainer with demo input.  
3) Generate a sample EN checklist (apps/py_checklist_generator/demo_checklist.md).

## 5. Metrics (for real clinics)

For each session/month, we plan to track anonymized counts, for example:

- MFA enabled on Google / WhatsApp (before → after).  
- Screen lock set.  
- Bank daily limit set/updated.  
- Scam-SMS identification score (5 examples, before vs after).  
- 1-week retention of changes.

Raw passwords, OTPs, or bank details are never recorded.
