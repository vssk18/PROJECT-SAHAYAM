import csv
import random
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "metrics" / "baseline_vs_week1.csv"

HEADER = [
    "session_id","participant_code","participant_type","age_group","language",
    "mfa_before","mfa_after",
    "screen_lock_before","screen_lock_after",
    "bank_limit_before","bank_limit_after",
    "scam_quiz_score_before","scam_quiz_score_after",
    "used_public_wifi","has_home_wifi_issues",
    "scanned_unknown_qr","used_public_qr_for_payment",
    "installed_unknown_apps","os_out_of_date",
    "inserted_unknown_usb","used_public_usb_charger",
    "shares_device_without_lock","password_reuse",
    "has_password_manager","fell_for_social_link_or_call",
    "risk_score_before","risk_score_after",
    "risk_category_before","risk_category_after",
    "date","notes",
]

def yes() -> int:
    return 1

def no() -> int:
    return 0

def risk_category(score: int) -> str:
    if score <= 3:
        return "low"
    if score <= 7:
        return "medium"
    return "high"

def sample_student_age() -> str:
    # simple ranges like "18-22"
    base = random.randint(18, 24)
    return f"{base}-{base+3}"

def sample_senior_age() -> str:
    base = random.choice([50, 55, 60, 65, 70])
    return f"{base}-{base+5}"

def generate_person(code: str, p_type: str, day: datetime.date) -> dict:
    """
    Generate one synthetic participant with sane patterns.
    We bias students and seniors a bit differently.
    """
    row = {}
    row["session_id"] = day.isoformat()
    row["participant_code"] = code
    row["participant_type"] = p_type
    row["language"] = "en"  # keep simple in the CSV

    if p_type == "student":
        row["age_group"] = sample_student_age()
    else:
        row["age_group"] = sample_senior_age()

    # --- BEFORE clinic ---
    # Protections: mix of good and bad
    if p_type == "student":
        mfa_before = random.choices([1, 0], weights=[4, 6])[0]
        screen_before = random.choices([1, 0], weights=[7, 3])[0]
        bank_before = random.choices([1, 0], weights=[3, 7])[0]
        scam_before = random.randint(1, 4)
    else:
        # seniors
        mfa_before = random.choices([1, 0], weights=[3, 7])[0]
        screen_before = random.choices([1, 0], weights=[6, 4])[0]
        bank_before = random.choices([1, 0], weights=[4, 6])[0]
        scam_before = random.randint(0, 3)

    row["mfa_before"] = mfa_before
    row["screen_lock_before"] = screen_before
    row["bank_limit_before"] = bank_before
    row["scam_quiz_score_before"] = scam_before

    # Risky habits
    used_public_wifi         = yes() if random.random() < 0.55 else no()
    has_home_wifi_issues     = yes() if random.random() < 0.35 else no()
    scanned_unknown_qr       = yes() if random.random() < 0.40 else no()
    used_public_qr_payment   = yes() if random.random() < 0.30 else no()
    installed_unknown_apps   = yes() if random.random() < 0.30 else no()
    os_out_of_date           = yes() if random.random() < 0.45 else no()
    inserted_unknown_usb     = yes() if random.random() < 0.30 else no()
    used_public_usb_charger  = yes() if random.random() < 0.40 else no()
    shares_device_without_lock = yes() if random.random() < 0.35 else no()
    password_reuse           = yes() if random.random() < 0.65 else no()
    has_password_manager     = yes() if random.random() < 0.15 else no()
    fell_for_social          = yes() if random.random() < 0.25 else no()

    # Save risk factors
    row["used_public_wifi"]        = used_public_wifi
    row["has_home_wifi_issues"]    = has_home_wifi_issues
    row["scanned_unknown_qr"]      = scanned_unknown_qr
    row["used_public_qr_for_payment"] = used_public_qr_payment
    row["installed_unknown_apps"]  = installed_unknown_apps
    row["os_out_of_date"]          = os_out_of_date
    row["inserted_unknown_usb"]    = inserted_unknown_usb
    row["used_public_usb_charger"] = used_public_usb_charger
    row["shares_device_without_lock"] = shares_device_without_lock
    row["password_reuse"]          = password_reuse
    row["has_password_manager"]    = has_password_manager
    row["fell_for_social_link_or_call"] = fell_for_social

    # --- Compute BEFORE risk score (0–10) ---
    risk = 0
    # lack of protections
    if mfa_before == 0:       risk += 2
    if screen_before == 0:    risk += 2
    if bank_before == 0:      risk += 1
    # knowledge
    if scam_before <= 1:      risk += 1
    # habits
    risk += used_public_wifi
    risk += has_home_wifi_issues
    risk += scanned_unknown_qr
    risk += used_public_qr_payment
    risk += installed_unknown_apps
    risk += os_out_of_date
    risk += inserted_unknown_usb
    risk += used_public_usb_charger
    risk += shares_device_without_lock
    risk += password_reuse
    risk += fell_for_social
    # some relief if they already have a manager
    if has_password_manager == 1:
        risk -= 1

    if risk < 0:
        risk = 0
    if risk > 10:
        risk = 10

    risk_before = risk
    row["risk_score_before"] = risk_before
    row["risk_category_before"] = risk_category(risk_before)

    # --- AFTER clinic (we assume some improvement) ---
    # Keep MFA the same or flip 0 -> 1 with some probability
    if mfa_before == 0 and random.random() < 0.7:
        mfa_after = 1
    else:
        mfa_after = mfa_before

    # Screen lock: often turns on
    if screen_before == 0 and random.random() < 0.8:
        screen_after = 1
    else:
        screen_after = screen_before

    # Bank limit: often improved for seniors
    if bank_before == 0 and random.random() < (0.7 if p_type == "senior" else 0.5):
        bank_after = 1
    else:
        bank_after = bank_before

    scam_after = max(scam_before, min(5, scam_before + random.randint(1, 3)))

    row["mfa_after"] = mfa_after
    row["screen_lock_after"] = screen_after
    row["bank_limit_after"] = bank_after
    row["scam_quiz_score_after"] = scam_after

    # Risk after: drop by 1–4 points with some noise
    drop = random.randint(1, 4)
    risk_after = max(0, risk_before - drop)
    row["risk_score_after"] = risk_after
    row["risk_category_after"] = risk_category(risk_after)

    row["date"] = day.isoformat()
    row["notes"] = ""

    return row

def main():
    random.seed(44)
    today = datetime.date.today()

    # around 220 students + 80 seniors = 300 total
    students = 220
    seniors = 80

    rows = []

    for i in range(1, students + 1):
        code = f"S{str(i).zfill(3)}"
        day = today - datetime.timedelta(days=random.randint(0, 20))
        rows.append(generate_person(code, "student", day))

    for i in range(1, seniors + 1):
        code = f"C{str(i).zfill(3)}"
        day = today - datetime.timedelta(days=random.randint(0, 20))
        rows.append(generate_person(code, "senior", day))

    # shuffle so students and seniors are mixed
    random.shuffle(rows)

    METRICS.parent.mkdir(parents=True, exist_ok=True)
    with METRICS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print("Written synthetic metrics to", METRICS)
    print("Total rows:", len(rows))

if __name__ == "__main__":
    main()
