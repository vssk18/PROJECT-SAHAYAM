import csv
import datetime
import subprocess
import sys
from pathlib import Path

from risk_explanations import (
    build_exposure_lines,
    build_protection_lines,
    build_next_steps_lines,
)

ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "metrics" / "baseline_vs_week1.csv"
GEN_DIR = ROOT / "materials" / "generated"

FIELDS = [
    "session_id","participant_code","participant_type","age_group","language",
    "mfa_before","mfa_after",
    "screen_lock_before","screen_lock_after",
    "bank_limit_before","bank_limit_after",
    "scam_quiz_score_before","scam_quiz_score_after",
    "used_public_wifi","has_home_wifi_issues",
    "scanned_unknown_qr","used_public_qr_for_payment",
    "installed_unknown_apps","os_out_of_date",
    "inserted_unknown_usb","used_public_usb_charger",
    "shares_device_without_lock","password_reuse","has_password_manager",
    "fell_for_social_link_or_call",
    "risk_score_before","risk_score_after",
    "risk_category_before","risk_category_after",
    "date","notes"
]

# --------------- helpers for input -----------------

def yes_no_int(prompt: str) -> int:
    while True:
        ans = input(prompt + "  yes or no  ").strip().lower()
        if ans in ("yes", "y"):
            return 1
        if ans in ("no", "n"):
            return 0
        print("Please type yes or no")

def score_int(prompt: str, minimum: int = 0, maximum: int = 5) -> int:
    while True:
        ans = input(f"{prompt}  number between {minimum} and {maximum}  ").strip()
        if ans.isdigit():
            val = int(ans)
            if minimum <= val <= maximum:
                return val
        print(f"Please type a number from {minimum} to {maximum}")

def next_participant_code() -> str:
    """
    Look at the metrics csv and generate P001, P002, ...
    based on the highest existing P-number.
    """
    if not METRICS_PATH.exists() or METRICS_PATH.stat().st_size == 0:
        return "P001"

    max_num = 0
    try:
        with METRICS_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = (row.get("participant_code") or "").strip()
                if code.startswith("P") and code[1:].isdigit():
                    n = int(code[1:])
                    if n > max_num:
                        max_num = n
    except Exception:
        # if anything goes wrong, fall back to first code
        return "P001"

    return f"P{max_num+1:03d}"

# --------------- risk model ------------------------

def compute_risk(mfa: int,
                 screen: int,
                 bank_limit: int,
                 scam_score: int,
                 used_public_wifi: int,
                 has_home_wifi_issues: int,
                 scanned_unknown_qr: int,
                 used_public_qr_payment: int,
                 installed_unknown_apps: int,
                 os_out_of_date: int,
                 inserted_unknown_usb: int,
                 used_public_usb_charger: int,
                 shares_device_without_lock: int,
                 password_reuse: int,
                 has_password_manager: int,
                 social_link_or_call: int) -> int:
    score = 10

    if mfa == 1:
        score -= 3
    if screen == 1:
        score -= 2
    if bank_limit == 1:
        score -= 2
    if scam_score >= 4:
        score -= 2
    if has_password_manager == 1:
        score -= 1

    score += used_public_wifi * 2
    score += has_home_wifi_issues * 2
    score += scanned_unknown_qr * 2
    score += used_public_qr_payment * 2
    score += installed_unknown_apps * 2
    score += os_out_of_date * 1
    score += inserted_unknown_usb * 1
    score += used_public_usb_charger * 1
    score += shares_device_without_lock * 1
    score += password_reuse * 2
    score += social_link_or_call * 2

    if score < 0:
        score = 0
    if score > 10:
        score = 10
    return score

def risk_category(score: int) -> str:
    if score <= 3:
        return "low"
    if score <= 6:
        return "medium"
    return "high"

# --------------- metrics writing -------------------

def append_metrics(row: dict):
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = METRICS_PATH.exists() and METRICS_PATH.stat().st_size > 0
    with METRICS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# --------------- checklist wrapper -----------------

def run_checklist_generator(name: str,
                            phone_last4: str,
                            lang_code: str,
                            apps_str: str,
                            limit: str,
                            participant_code: str):
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out_file = GEN_DIR / f"checklist_{participant_code}.{lang_code}.md"
    script = ROOT / "apps" / "py_checklist_generator" / "generate_checklist.py"
    cmd = [
        sys.executable,
        str(script),
        "--name", name,
        "--phone", phone_last4,
        "--apps", apps_str,
        "--limit", limit,
        "--lang", lang_code,
        "--out", str(out_file)
    ]
    print("Running checklist generator")
    subprocess.run(cmd, check=True)
    print("Checklist saved in", out_file)

# --------------- detailed report -------------------

def generate_report(participant_code: str,
                    name: str,
                    lang_code: str,
                    before_score: int,
                    after_score: int,
                    before_cat: str,
                    after_cat: str,
                    answers: dict):
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out_file = GEN_DIR / f"report_{participant_code}.{lang_code}.md"

    exposure_lines = build_exposure_lines(answers)
    protection_lines = build_protection_lines(answers)
    next_step_lines = build_next_steps_lines(answers, after_cat)

    with out_file.open("w", encoding="utf-8") as r:
        r.write(f"# SAHAYAM security report for {participant_code}\n\n")
        if name:
            r.write(f"Name for clinic record  {name}\n\n")

        r.write("## Summary of this visit\n")
        r.write(f"- Estimated risk before the clinic  {before_score} out of 10  category  {before_cat}\n")
        r.write(f"- Estimated risk after the clinic   {after_score} out of 10  category  {after_cat}\n")
        change = before_score - after_score
        if change > 0:
            r.write(f"- Change in this visit  risk reduced by {change} points based on the answers and checks\n\n")
        elif change == 0:
            r.write("- Change in this visit  risk stayed the same based on the answers and checks\n\n")
        else:
            r.write(f"- Change in this visit  risk increased by {-change} points based on the answers and checks\n\n")
        r.write("This score is not a guarantee or a formal audit  it is a guide built from your own answers and quick checks.\n\n")

        r.write("## Areas covered in this report\n")
        r.write("- Phone basics such as lock screen and updates\n")
        r.write("- Extra login protection such as two step verification\n")
        r.write("- Banking and upi daily limits\n")
        r.write("- Public wifi and home wifi\n")
        r.write("- QR code payments and random qr scans\n")
        r.write("- Apps from outside the store and pending updates\n")
        r.write("- Usb devices and public usb charging\n")
        r.write("- Password reuse and password manager use\n")
        r.write("- Scam messages links and urgent calls\n\n")

        r.write("## Where your device and accounts are open to attack\n")
        for line in exposure_lines:
            r.write(f"- {line}\n")
        r.write("\n")

        r.write("## Protections that are already helping you\n")
        for line in protection_lines:
            r.write(f"- {line}\n")
        r.write("\n")

        r.write("## What this risk level means in daily life\n")
        if after_cat == "high":
            r.write("High risk means that with the current habits and settings a common scam or simple technical attack can still work.\n")
            r.write("You should treat this report as a work list and change one habit at a time until most of the exposure points are fixed.\n\n")
        elif after_cat == "medium":
            r.write("Medium risk means some protections are in place but there are still clear gaps that attackers can use.\n")
            r.write("With a few focused changes you can bring this closer to low risk.\n\n")
        else:
            r.write("Low risk means you have covered many basic protections and have better habits than most people.\n")
            r.write("Still keep an eye on new fraud patterns and repeat this check at times.\n\n")

        r.write("## Next steps for the coming week\n")
        for line in next_step_lines:
            r.write(line + "\n")
        r.write("\n")

        r.write("## When to ask for help right away\n")
        r.write("- If money moves without your clear action  call your bank helpline or the official number inside the bank app.\n")
        r.write("- If you shared one time password card number or pin by mistake  call the bank at once and ask them to block and review.\n")
        r.write("- For online fraud or suspicious messages and links you can raise a complaint on the National Cyber Crime Portal  https://cybercrime.gov.in\n")
        r.write("- In many parts of India you can also call the cyber fraud helpline  1930  where it is active.\n\n")

        r.write("## Reminder\n")
        r.write("This report is based on your answers in one clinic visit and on the quick checks done in that time.\n")
        r.write("Keep it with your one page checklist and update both as your habits improve.\n")

    print("Report saved in", out_file)

# --------------- main flow -------------------------

def main():
    print("=== SAHAYAM clinic assistant  custom risk and report ===")
    print("This tool checks")
    print("1  screen lock and phone basics")
    print("2  extra login protection such as two step verification")
    print("3  bank and upi daily limits")
    print("4  public wifi and home wifi")
    print("5  qr code payments and unknown qr codes")
    print("6  apps from outside the store and pending updates")
    print("7  usb devices and public usb charging")
    print("8  password reuse and password manager use")
    print("9  scam messages links and urgent calls\n")

    today = datetime.date.today().isoformat()
    session_id = input(f"Session id  press enter for {today}  ").strip() or today

    # auto-generate participant code
    participant_code = next_participant_code()
    print(f"Generated code for this person  {participant_code}")

    participant_type = input("Type of participant  senior citizen or engineering student  ").strip().lower()
    age_group = input("Age group  for example 18 to 25 or 50 to 60 or 60 to 75  ").strip()
    # language fixed to English for now
    lang_code = "en"
    name = input("Name for checklist  you can also leave this empty  ").strip()
    phone_last4 = input("Last four digits of phone number  only for checklist print  ").strip()

    print("\nPart 1  protections already on this phone and in accounts\n")
    mfa_before = yes_no_int("Is extra login protection like two step or otp already on for any important account")
    screen_before = yes_no_int("Is there already a lock on this phone such as pin pattern or fingerprint")
    bank_before = yes_no_int("Is there already a safe daily limit set in your banking or upi app")
    scam_before = score_int("Out of five sample sms or chat messages how many scams can you catch right now", 0, 5)

    print("\nPart 2  wifi and network use\n")
    used_public_wifi = yes_no_int("In the last month have you connected this phone or laptop to public or free wifi in places like cafe station or mall")
    has_home_wifi_issues = yes_no_int("Does your home wifi still use a default or very simple password or an old router setting")

    print("\nPart 3  qr code and payment habits\n")
    scanned_unknown_qr = yes_no_int("Have you scanned any qr code from posters papers or unknown forwards in chat")
    used_public_qr_payment = yes_no_int("Have you paid through qr without fully checking the name and amount on the payment screen")

    print("\nPart 4  apps and updates\n")
    installed_unknown_apps = yes_no_int("Have you installed apps from outside the official store using files or links from others")
    os_out_of_date = yes_no_int("Are phone updates waiting for many weeks and not installed")

    print("\nPart 5  usb devices and charging\n")
    inserted_unknown_usb = yes_no_int("Have you put pen drives or usb devices from other people into your laptop or pc")
    used_public_usb_charger = yes_no_int("Have you charged your phone from free public usb charging ports")

    print("\nPart 6  sharing and passwords\n")
    shares_device_without_lock = yes_no_int("Do you give your phone to others while it is open or without any lock")
    password_reuse = yes_no_int("Do you use the same password for many sites or apps")
    has_password_manager = yes_no_int("Do you use a password manager app or service")

    print("\nPart 7  scam messages and calls\n")
    fell_for_social_link_or_call = yes_no_int("Have you ever clicked a link or followed instructions in a call or chat about money kyc closure prize or refund and later felt it was suspicious")

    print("\nNow you run the teaching part for this person  phone settings sms and link demo qr demo password habits\n")
    input("When you finish teaching and changes are done press enter to continue  ")

    print("\nNow we note the state after your help\n")
    mfa_after = yes_no_int("Is extra login protection like two step or otp now enabled on at least one important account")
    screen_after = yes_no_int("Is a lock now set on this phone")
    bank_after = yes_no_int("Is a safe daily bank or upi limit now set or checked again")
    scam_after = score_int("Out of the same five example messages how many scams can you now catch", 0, 5)

    before_score = compute_risk(
        mfa_before, screen_before, bank_before, scam_before,
        used_public_wifi, has_home_wifi_issues,
        scanned_unknown_qr, used_public_qr_payment,
        installed_unknown_apps, os_out_of_date,
        inserted_unknown_usb, used_public_usb_charger,
        shares_device_without_lock, password_reuse,
        has_password_manager, fell_for_social_link_or_call
    )
    after_score = compute_risk(
        mfa_after, screen_after, bank_after, scam_after,
        used_public_wifi, has_home_wifi_issues,
        scanned_unknown_qr, used_public_qr_payment,
        installed_unknown_apps, os_out_of_date,
        inserted_unknown_usb, used_public_usb_charger,
        shares_device_without_lock, password_reuse,
        has_password_manager, fell_for_social_link_or_call
    )

    cat_before = risk_category(before_score)
    cat_after = risk_category(after_score)

    today_str = datetime.date.today().isoformat()
    notes = input("Short notes about this session  optional  ").strip()

    row = {
        "session_id": session_id,
        "participant_code": participant_code,
        "participant_type": participant_type,
        "age_group": age_group,
        "language": lang_code,
        "mfa_before": mfa_before,
        "mfa_after": mfa_after,
        "screen_lock_before": screen_before,
        "screen_lock_after": screen_after,
        "bank_limit_before": bank_before,
        "bank_limit_after": bank_after,
        "scam_quiz_score_before": scam_before,
        "scam_quiz_score_after": scam_after,
        "used_public_wifi": used_public_wifi,
        "has_home_wifi_issues": has_home_wifi_issues,
        "scanned_unknown_qr": scanned_unknown_qr,
        "used_public_qr_for_payment": used_public_qr_payment,
        "installed_unknown_apps": installed_unknown_apps,
        "os_out_of_date": os_out_of_date,
        "inserted_unknown_usb": inserted_unknown_usb,
        "used_public_usb_charger": used_public_usb_charger,
        "shares_device_without_lock": shares_device_without_lock,
        "password_reuse": password_reuse,
        "has_password_manager": has_password_manager,
        "fell_for_social_link_or_call": fell_for_social_link_or_call,
        "risk_score_before": before_score,
        "risk_score_after": after_score,
        "risk_category_before": cat_before,
        "risk_category_after": cat_after,
        "date": today_str,
        "notes": notes
    }

    append_metrics(row)
    print("\nSaved metrics for", participant_code)
    print("Risk before  ", before_score, " out of 10  ", cat_before)
    print("Risk after   ", after_score, " out of 10  ", cat_after)

    apps_str = "Google, WhatsApp, Bank"
    limit = "₹5,000"
    phone_display = "XXXX" + phone_last4 if phone_last4 else "XXXXXXXX"

    print("\nCreating one page checklist for this person")
    run_checklist_generator(
        name=name or f"Participant {participant_code}",
        phone_last4=phone_display,
        lang_code=lang_code,
        apps_str=apps_str,
        limit=limit,
        participant_code=participant_code
    )

    answers = {
        "mfa_after": mfa_after,
        "screen_after": screen_after,
        "bank_after": bank_after,
        "scam_after": scam_after,
        "used_public_wifi": used_public_wifi,
        "has_home_wifi_issues": has_home_wifi_issues,
        "scanned_unknown_qr": scanned_unknown_qr,
        "used_public_qr_for_payment": used_public_qr_payment,
        "installed_unknown_apps": installed_unknown_apps,
        "os_out_of_date": os_out_of_date,
        "inserted_unknown_usb": inserted_unknown_usb,
        "used_public_usb_charger": used_public_usb_charger,
        "shares_device_without_lock": shares_device_without_lock,
        "password_reuse": password_reuse,
        "has_password_manager": has_password_manager,
        "fell_for_social_link_or_call": fell_for_social_link_or_call
    }

    print("Creating detailed security report for this person\n")
    generate_report(
        participant_code=participant_code,
        name=name,
        lang_code=lang_code,
        before_score=before_score,
        after_score=after_score,
        before_cat=cat_before,
        after_cat=cat_after,
        answers=answers
    )

    print("Clinic run complete for", participant_code)
    print("Checklist and report are stored in", GEN_DIR)

if __name__ == "__main__":
    main()
