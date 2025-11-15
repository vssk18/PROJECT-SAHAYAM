import subprocess
import sys
import datetime
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "metrics" / "baseline_vs_week1.csv"
CHECKLIST_DIR = ROOT / "materials" / "generated"
REPORT_DIR = ROOT / "materials" / "generated"

FIELDS = [
    "session_id","participant_code","participant_type","age_group","language",
    "mfa_before","mfa_after","screen_lock_before","screen_lock_after",
    "bank_limit_before","bank_limit_after","scam_quiz_score_before","scam_quiz_score_after",
    "used_public_wifi","scanned_unknown_qr","inserted_unknown_usb","fell_for_social_link",
    "risk_score_before","risk_score_after","date","notes"
]

def yes_no_int(prompt: str) -> int:
    while True:
        ans = input(prompt + " (yes/no): ").strip().lower()
        if ans in ("yes","y"):
            return 1
        if ans in ("no","n"):
            return 0
        print("Please answer yes or no.")

def score_int(prompt: str, minimum: int = 0, maximum: int = 5) -> int:
    while True:
        ans = input(f"{prompt} (integer {minimum}-{maximum}): ").strip()
        if ans.isdigit():
            val = int(ans)
            if minimum <= val <= maximum:
                return val
        print(f"Enter an integer between {minimum} and {maximum}.")

def compute_risk(mfa_after, screen_after, bank_after, scam_after, wifi_risk, qr_risk, usb_risk, social_risk):
    score = 10
    if mfa_after == 1:
        score -= 3
    if screen_after == 1:
        score -= 2
    if bank_after == 1:
        score -= 2
    if scam_after >= 4:
        score -= 2
    # additional vectors
    if wifi_risk == 1:
        score += 2
    if qr_risk == 1:
        score += 2
    if usb_risk == 1:
        score += 1
    if social_risk == 1:
        score += 1
    if score < 0:
        score = 0
    if score > 10:
        score = 10
    return score

def append_metrics(row: dict):
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = METRICS_PATH.exists() and METRICS_PATH.stat().st_size > 0
    with METRICS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def generate_checklist(name: str, phone_last4: str, language: str, apps_str: str, limit: str, participant_code: str):
    CHECKLIST_DIR.mkdir(parents=True, exist_ok=True)
    out_file = CHECKLIST_DIR / f"checklist_{participant_code}.{language}.md"
    script = ROOT / "apps" / "py_checklist_generator" / "generate_checklist.py"
    cmd = [
        sys.executable,
        str(script),
        "--name", name,
        "--phone", phone_last4,
        "--apps", apps_str,
        "--limit", limit,
        "--lang", language,
        "--out", str(out_file)
    ]
    print("Running checklist generator:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("Checklist written to", out_file)

def generate_report(participant_code: str, name: str, language: str,
                    before_risk: int, after_risk: int,
                    wifi_risk: int, qr_risk: int, usb_risk: int, social_risk: int):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"report_{participant_code}.{language}.md"
    with report_file.open("w", encoding="utf-8") as r:
        r.write(f"# SAHAYAM Security Report — Participant {participant_code}\n\n")
        r.write(f"Name (for checklist): {name}\n\n")
        r.write(f"Risk Score — Before: {before_risk}/10  |  After: {after_risk}/10\n\n")
        r.write("## Key Risk Vectors Identified\n")
        if wifi_risk:
            r.write("- ✅ Connected to public or unknown Wi-Fi network\n")
        if qr_risk:
            r.write("- ✅ Scanned unknown or unverified QR code\n")
        if usb_risk:
            r.write("- ✅ Inserted or used a USB/device from an unknown source\n")
        if social_risk:
            r.write("- ✅ Clicked link or shared OTP/credentials from social message\n")
        r.write("\n## What You Did Right\n")
        if after_risk < before_risk:
            r.write(f"You reduced your risk score by {before_risk-after_risk} points. Well done!\n\n")
        r.write("## Recommendations & Good Habits\n")
        r.write("- Use Wi-Fi only from trusted networks; avoid conducting banking or payments on public/free Wi-Fi.  [oai_citation:0‡Hindustan Times](https://www.hindustantimes.com/technology/indian-government-warns-public-wi-fi-users-advises-avoiding-these-mistakes-101745823515237.html?utm_source=chatgpt.com)\n")
        r.write("- Before scanning any QR code in a shop or online, check that the recipient name matches and the sticker has not been tampered with.  [oai_citation:1‡The Times of India](https://timesofindia.indiatimes.com/city/bhopal/khajuraho-traders-in-shock-as-scammers-replace-qr-codes-outside-shops-overnight-to-redirect-payments/articleshow/117190197.cms?utm_source=chatgpt.com)\n")
        r.write("- Do not insert USBs or devices from unknown sources; treat all unknown storage media as potentially malicious.\n")
        r.write("- Always enable screen lock and multi-factor authentication for key accounts.\n")
        r.write("- Set a safe daily limit for your banking/UPI transactions.\n")
        r.write("- Test yourself by identifying at least 4 out of 5 scam SMS/links each week.\n")
        r.write("\n## Cautions & Things to Avoid\n")
        r.write("- Never share OTPs, PINs or verification codes with anyone.\n")
        r.write("- Do not respond to messages asking you to ‘verify your account’ via links or QR codes.\n")
        r.write("- Avoid scanning QR codes in public places where the code could have been replaced.  [oai_citation:2‡The Times of India](https://timesofindia.indiatimes.com/city/jaipur/cops-warn-against-fake-qr-code-fraud/articleshow/121631302.cms?utm_source=chatgpt.com)\n")
        r.write("- Do not connect your phone/laptop to unknown charging ports or free USB-chargers in public places.\n")
        r.write("\n## Helplines & Reporting (India)\n")
        r.write("- To report cyber fraud, visit: https://cybercrime.gov.in\n")
        r.write("- If you suspect a fake UPI payment QR, contact your bank immediately.\n")
        r.write("- For police complaints: Dial 1930 (National Cyber Crime Reporting Portal) or your state cybercrime helpline.\n")
    print("Report generated:", report_file)

def main():
    print("=== SAHAYAM Clinic Assistant (Extended) ===")
    today = datetime.date.today().isoformat()
    session_id = input(f"Session id [default {today}]: ").strip() or today
    participant_code = input("Participant code (e.g., P001): ").strip()
    participant_type = input("Participant type (senior citizen / engineering student): ").strip().lower()
    age_group = input("Age group (e.g., 18-25, 50-60): ").strip()
    language = input("Language (english / telugu / hindi): ").strip().lower() or "english"
    name = input("Participant name (for checklist only): ").strip()
    phone_last4 = input("Phone last four digits (for checklist only, e.g., 1234): ").strip()

    print("\n--- BEFORE CLINIC ---")
    mfa_before = yes_no_int("Is multi-factor authentication already enabled on an important account?")
    screen_before = yes_no_int("Is a screen lock already enabled on this device?")
    bank_before = yes_no_int("Is a safe daily bank/UPI transaction limit already set?")
    scam_before = score_int("Scam detection score BEFORE clinic (out of 5 examples)")
    wifi_risk = yes_no_int("Did you recently connect to a public or unknown Wi-Fi network on this device?")
    qr_risk = yes_no_int("Did you scan an unknown or unverified QR code in the past 30 days?")
    usb_risk = yes_no_int("Have you used a USB or storage device from someone you do not fully trust?")
    social_risk = yes_no_int("Have you clicked a link or shared a code/OTP from a message or WhatsApp that seemed urgent?")

    print("\nPlease perform the teaching session (phone hardening, SMS/URL/QR demos, passphrase trainer). Then press Enter.")
    input("Press Enter to continue...")

    print("\n--- AFTER CLINIC ---")
    mfa_after = yes_no_int("Is multi-factor authentication now enabled on an important account?")
    screen_after = yes_no_int("Is a screen lock now enabled on this device?")
    bank_after = yes_no_int("Is the safe daily bank/UPI transaction limit now set/adjusted?")
    scam_after = score_int("Scam detection score AFTER clinic (out of 5 examples)")

    before_risk = compute_risk(mfa_before, screen_before, bank_before, scam_before,
                               wifi_risk, qr_risk, usb_risk, social_risk)
    after_risk = compute_risk(mfa_after, screen_after, bank_after, scam_after,
                              0, 0, 0, 0)
    today_str = today
    notes = input("Short notes about this session (optional): ").strip()

    row = {
        "session_id": session_id,
        "participant_code": participant_code,
        "participant_type": participant_type,
        "age_group": age_group,
        "language": language,
        "mfa_before": mfa_before,
        "mfa_after": mfa_after,
        "screen_lock_before": screen_before,
        "screen_lock_after": screen_after,
        "bank_limit_before": bank_before,
        "bank_limit_after": bank_after,
        "scam_quiz_score_before": scam_before,
        "scam_quiz_score_after": scam_after,
        "used_public_wifi": wifi_risk,
        "scanned_unknown_qr": qr_risk,
        "inserted_unknown_usb": usb_risk,
        "fell_for_social_link": social_risk,
        "risk_score_before": before_risk,
        "risk_score_after": after_risk,
        "date": today_str,
        "notes": notes
    }

    append_metrics(row)
    print(f"\nSaved metrics row for participant {participant_code}")
    print(f"Risk score — before: {before_risk}/10, after: {after_risk}/10")

    print("\n--- Generating personalised checklist ---")
    apps_str = "Google, WhatsApp, Bank"
    limit = "₹5,000"
    generate_checklist(name=name, phone_last4="XXXX"+phone_last4, language=language, apps_str=apps_str, limit=limit, participant_code=participant_code)

    print("--- Generating full security report ---")
    generate_report(participant_code, name, language, before_risk, after_risk, wifi_risk, qr_risk, usb_risk, social_risk)

    print(f"\nClinic session for {participant_code} complete. Checklist + report ready in materials/generated.")
