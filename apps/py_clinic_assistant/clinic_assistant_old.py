import subprocess
import sys
import datetime
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "metrics" / "baseline_vs_week1.csv"
CHECKLIST_DIR = ROOT / "materials" / "generated"

FIELDS = [
    "session_id","participant_code","participant_type","age_group","language",
    "mfa_before","mfa_after","screen_lock_before","screen_lock_after",
    "bank_limit_before","bank_limit_after","scam_quiz_score_before","scam_quiz_score_after",
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

def compute_risk(mfa_after, screen_after, bank_after, scam_after):
    score = 10
    if mfa_after == 1:
        score -= 3
    if screen_after == 1:
        score -= 2
    if bank_after == 1:
        score -= 2
    if scam_after >= 4:
        score -= 3
    if score < 0:
        score = 0
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

def main():
    print("=== SAHAYAM Clinic Assistant ===")
    today = datetime.date.today().isoformat()
    session_id = input(f"Session id [default {today}]: ").strip() or today
    participant_code = input("Participant code (e.g., P001): ").strip()
    participant_type = input("Participant type (senior citizen / engineering student): ").strip().lower()
    age_group = input("Age group (e.g., 18-25, 50-60): ").strip()
    language = input("Language (english / telugu / hindi): ").strip().lower() or "english"
    name = input("Participant name (for checklist only): ").strip()
    phone_last4 = input("Phone last four digits (for checklist only, e.g., 1234): ").strip()

    print("\n--- BEFORE CLINIC ---")
    mfa_before = yes_no_int("Is multi-factor authentication (two-step verification) already enabled on an important account?")
    screen_before = yes_no_int("Is a screen lock (PIN/pattern/fingerprint) already enabled on this device?")
    bank_before = yes_no_int("Is a safe daily transaction limit already set in your banking app?")
    scam_before = score_int("Scam detection score BEFORE clinic (out of 5 examples)")

    print("\nPlease conduct your teaching: phone hardening, SMS/URL/QR demos, passphrase trainer. Then press Enter.")
    input("Press Enter when ready to proceed to AFTER section...")

    print("\n--- AFTER CLINIC ---")
    mfa_after = yes_no_int("Is multi-factor authentication now enabled on an important account?")
    screen_after = yes_no_int("Is a screen lock now enabled on this device?")
    bank_after = yes_no_int("Is a safe daily limit now set/adjusted in your banking app?")
    scam_after = score_int("Scam detection score AFTER clinic (out of 5 examples)")

    risk_before = compute_risk(mfa_before, screen_before, bank_before, scam_before)
    risk_after = compute_risk(mfa_after, screen_after, bank_after, scam_after)

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
        "risk_score_before": risk_before,
        "risk_score_after": risk_after,
        "date": today_str,
        "notes": notes
    }

    append_metrics(row)
    print(f"\nSaved metrics row for participant {participant_code}")
    print(f"Risk score — before: {risk_before}/10, after: {risk_after}/10")

    print("\n--- Generating personalised checklist ---")
    apps_str = "Google, WhatsApp, Bank"
    limit = "₹5,000"
    generate_checklist(name=name, phone_last4="XXXX"+phone_last4, language=language, apps_str=apps_str, limit=limit, participant_code=participant_code)
    print(f"Checklist ready for {participant_code}")
