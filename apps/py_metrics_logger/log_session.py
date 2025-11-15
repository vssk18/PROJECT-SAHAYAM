import csv
import datetime
from pathlib import Path

METRICS_PATH = Path(__file__).resolve().parents[2] / "metrics" / "baseline_vs_week1.csv"

FIELDS = [
    "session_id","participant_code","age_group","lang",
    "mfa_before","mfa_after",
    "screenlock_before","screenlock_after",
    "banklimit_before","banklimit_after",
    "scam_score_before","scam_score_after",
    "date","notes"
]

def yes_no_to_int(prompt: str) -> int:
    while True:
        ans = input(prompt + " (y/n): ").strip().lower()
        if ans in ("y","yes"):
            return 1
        if ans in ("n","no"):
            return 0
        print("Please type y or n.")

def score_input(prompt: str, minimum: int = 0, maximum: int = 5) -> int:
    while True:
        ans = input(f"{prompt} ({minimum}-{maximum}): ").strip()
        if ans.isdigit():
            val = int(ans)
            if minimum <= val <= maximum:
                return val
        print(f"Enter an integer between {minimum} and {maximum}.")

def main():
    print("=== SAHAYAM metrics logger ===")
    print(f"Metrics file: {METRICS_PATH}")
    print()

    session_id = input("Session id (e.g., 2024-11-17-morning): ").strip()
    participant_code = input("Participant code (e.g., P001): ").strip()
    age_group = input("Age group (50-60 / 60-70 / 70+): ").strip()
    lang = input("Language (en/te/hi): ").strip().lower() or "en"

    print("\n--- BEFORE CLINIC ---")
    mfa_before = yes_no_to_int("MFA already enabled on main account?")
    screen_before = yes_no_to_int("Screen lock already enabled?")
    bank_before = yes_no_to_int("Bank daily limit already set?")
    scam_before = score_input("Scam SMS score BEFORE clinic (out of 5 examples)")

    print("\n--- AFTER CLINIC ---")
    mfa_after = yes_no_to_int("MFA enabled now?")
    screen_after = yes_no_to_int("Screen lock enabled now?")
    bank_after = yes_no_to_int("Bank daily limit set/adjusted now?")
    scam_after = score_input("Scam SMS score AFTER clinic (out of 5 examples)")

    today_str = datetime.date.today().isoformat()
    notes = input("Short notes (optional): ").strip()

    row = {
        "session_id": session_id,
        "participant_code": participant_code,
        "age_group": age_group,
        "lang": lang,
        "mfa_before": mfa_before,
        "mfa_after": mfa_after,
        "screenlock_before": screen_before,
        "screenlock_after": screen_after,
        "banklimit_before": bank_before,
        "banklimit_after": bank_after,
        "scam_score_before": scam_before,
        "scam_score_after": scam_after,
        "date": today_str,
        "notes": notes,
    }

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = METRICS_PATH.exists() and METRICS_PATH.stat().st_size > 0

    with METRICS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print("\nSaved row to", METRICS_PATH)

if __name__ == "__main__":
    main()
