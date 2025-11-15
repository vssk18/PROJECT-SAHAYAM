import csv
import datetime
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------
# 1. Paths and fixed fields
# --------------------------------------------------

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

# --------------------------------------------------
# 2. Small helper functions for input
# --------------------------------------------------

def yes_no_int(prompt: str) -> int:
    """Ask a yes/no question until we get a clear answer. Return 1 for yes, 0 for no."""
    while True:
        ans = input(prompt + "  yes or no  ").strip().lower()
        if ans in ("yes", "y"):
            return 1
        if ans in ("no", "n"):
            return 0
        print("Please type yes or no")

def score_int(prompt: str, minimum: int = 0, maximum: int = 5) -> int:
    """Ask for a small integer score in a range, for example number of scams caught."""
    while True:
        ans = input(f"{prompt}  number between {minimum} and {maximum}  ").strip()
        if ans.isdigit():
            val = int(ans)
            if minimum <= val <= maximum:
                return val
        print(f"Please type a number from {minimum} to {maximum}")

def normalise_language(raw: str) -> str:
    lang = (raw or "").strip().lower()
    if lang.startswith("en"):
        return "en"
    if lang.startswith("te"):
        return "te"
    if lang.startswith("hi"):
        return "hi"
    return "en"

# --------------------------------------------------
# 3. Risk model
# --------------------------------------------------

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
    """
    Simple rule based risk score.
    0 means low estimated risk, 10 means high estimated risk.
    This is not a formal audit, just a clear guide for teaching.
    """
    score = 10

    # Protections lower risk
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

    # Risky habits add risk
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

    # Keep inside 0 to 10
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

# --------------------------------------------------
# 4. Metrics writing
# --------------------------------------------------

def append_metrics(row: dict):
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = METRICS_PATH.exists() and METRICS_PATH.stat().st_size > 0
    with METRICS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# --------------------------------------------------
# 5. Checklist generator wrapper
# --------------------------------------------------

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

# --------------------------------------------------
# 6. Report generator
# --------------------------------------------------

def generate_report(participant_code: str,
                    name: str,
                    lang_code: str,
                    before_score: int,
                    after_score: int,
                    before_cat: str,
                    after_cat: str,
                    answers: dict):
    """
    Create a detailed markdown report for this person.
    Language is kept simple and direct so it can be read aloud.
    """
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out_file = GEN_DIR / f"report_{participant_code}.{lang_code}.md"

    with out_file.open("w", encoding="utf-8") as r:
        r.write(f"# SAHAYAM security report for {participant_code}\n\n")
        if name:
            r.write(f"Name for clinic record  {name}\n\n")

        # Summary
        r.write("## Summary of this visit\n")
        r.write(f"- Estimated risk before the clinic  {before_score} out of 10  category  {before_cat}\n")
        r.write(f"- Estimated risk after the clinic   {after_score} out of 10  category  {after_cat}\n")
        change = before_score - after_score
        if change > 0:
            r.write(f"- Change in this visit  risk reduced by {change} points based on the answers and settings checked\n\n")
        elif change == 0:
            r.write("- Change in this visit  risk stayed the same based on the answers and settings checked\n\n")
        else:
            r.write(f"- Change in this visit  risk increased by {-change} points based on the answers and settings checked\n\n")
        r.write("This score is not a guarantee or a formal audit  it is a simple guide built from your answers about real habits\n\n")

        # Areas checked
        r.write("## Areas checked in this report\n")
        r.write("- Phone basics  lock screen and updates\n")
        r.write("- Extra login protection  two step verification or app based codes\n")
        r.write("- Banking and UPI daily limits\n")
        r.write("- Public and home wifi\n")
        r.write("- QR codes for payment and random QR scans\n")
        r.write("- Apps from outside the store and pending updates\n")
        r.write("- USB devices and public USB charging\n")
        r.write("- Password reuse and password manager use\n")
        r.write("- Scam messages links and urgent calls\n\n")

        # Exposures
        r.write("## Where your device and accounts are exposed right now\n")
        a = answers
        any_exposure = False
        if a["used_public_wifi"]:
            any_exposure = True
            r.write("- You used public or free wifi in the last month  this can let others watch or change traffic if the network is not safe\n")
        if a["has_home_wifi_issues"]:
            any_exposure = True
            r.write("- Your home wifi may still have the default password or a very simple one  this makes it easier for neighbours or attackers to join your network\n")
        if a["scanned_unknown_qr"]:
            any_exposure = True
            r.write("- You scanned qr codes from posters or unknown forwards  a fake qr can change where money is sent or open risky sites\n")
        if a["used_public_qr_for_payment"]:
            any_exposure = True
            r.write("- You used qr codes for payment without reading the name and amount each time  this is how many upi frauds start\n")
        if a["installed_unknown_apps"]:
            any_exposure = True
            r.write("- You installed apps from outside the official store  such apps can ask for camera microphone sms or accessibility access without clear checks\n")
        if a["os_out_of_date"]:
            any_exposure = True
            r.write("- Your phone or apps have pending updates  missing updates means old security holes are still open\n")
        if a["inserted_unknown_usb"]:
            any_exposure = True
            r.write("- You plugged in usb drives or devices from other people  a bad device can bring malware or change system settings\n")
        if a["used_public_usb_charger"]:
            any_exposure = True
            r.write("- You used public usb charging points  some ports can try to read data while charging\n")
        if a["shares_device_without_lock"]:
            any_exposure = True
            r.write("- You give your phone to others while it is unlocked  anyone holding it can open apps read messages and reset accounts\n")
        if a["password_reuse"]:
            any_exposure = True
            r.write("- You reuse the same password on many sites  if one site leaks the password attackers can try it everywhere\n")
        if a["fell_for_social_link_or_call"]:
            any_exposure = True
            r.write("- You have followed instructions in messages or calls about money or kyc that later felt suspicious  this shows pressure from others can work on you\n")
        if not any_exposure:
            r.write("- In this session you did not report any major risky habit  keep reviewing this once in a while\n")
        r.write("\n")

        # Protections
        r.write("## Protections that are already in place or were added today\n")
        any_protection = False
        if a["mfa_after"]:
            any_protection = True
            r.write("- Extra login protection is on for at least one important account  this makes stolen passwords less useful\n")
        if a["screen_after"]:
            any_protection = True
            r.write("- A lock screen is set on your phone  this slows down anyone who picks up the phone\n")
        if a["bank_after"]:
            any_protection = True
            r.write("- A safe daily bank or upi limit is set or checked again  this reduces loss if one transaction goes wrong\n")
        if a["scam_after"] >= 4:
            any_protection = True
            r.write("- You can now spot most scam messages in a small quiz  this skill is important for every new fraud pattern\n")
        if a["has_password_manager"]:
            any_protection = True
            r.write("- You use a password manager  this reduces password reuse and makes long passwords possible\n")
        if not any_protection:
            r.write("- Today we did not confirm any strong protection  please follow the steps below with a trainer or trusted family member\n")
        r.write("\n")

        # Meaning of risk
        r.write("## What this risk level means in daily life\n")
        if after_cat == "high":
            r.write("- High means that with the current habits and settings it is easy for a common scam or simple technical attack to work\n")
            r.write("- Many of the habits above need to change step by step  you do not have to fix everything in one day but you should follow a plan\n\n")
        elif after_cat == "medium":
            r.write("- Medium means you have some protections but there are still clear weak spots that attackers can use\n\n")
        else:
            r.write("- Low means you have covered many basic checks  still keep an eye on new scams and update regularly\n\n")

        # Next steps
        r.write("## Next steps for the coming week\n")
        r.write("You do not need to do everything in one night  focus on these steps in order\n\n")
        if not a["screen_after"]:
            r.write("1  Set a simple screen lock today  pattern pin or fingerprint  do this before giving the phone to anyone else\n")
        if not a["mfa_after"]:
            r.write("2  Turn on extra login protection on your main email and bank account with the help of a trainer or trusted person\n")
        if not a["bank_after"]:
            r.write("3  Set a daily transfer limit in your bank app that is enough for normal life but not high enough for a big loss\n")
        if a["password_reuse"] and not a["has_password_manager"]:
            r.write("4  List your top three accounts  email bank and one more  change these to different passwords and store them safely\n")
        if a["os_out_of_date"] or a["installed_unknown_apps"]:
            r.write("5  Remove apps that you do not use or do not recognise  then run phone updates and app updates when you are on home wifi\n")
        if a["used_public_wifi"]:
            r.write("6  Decide a rule that banking and important logins happen only on mobile data or trusted home wifi  not on free wifi\n")
        if a["scanned_unknown_qr"] or a["used_public_qr_for_payment"]:
            r.write("7  For payments always read the name on the screen and the amount before you press pay  do not scan qr codes from random walls or forwards\n")
        if a["fell_for_social_link_or_call"]:
            r.write("8  Write a short reminder and keep it near the phone  for example  I will not share otp or click payment links from calls or unknown chat\n")
        r.write("\nIf some of these steps feel difficult you can bring this report to the next clinic session or to a trusted engineering student or family member and work through it together\n\n")

        # Help section
        r.write("## When to call for help\n")
        r.write("- If you think money has moved without your clear action  call your bank helpline or the official number in the bank app\n")
        r.write("- If you shared otp card number or pin by mistake  call the bank at once and ask them to block and review\n")
        r.write("- For online fraud or suspicious messages and links you can raise a complaint on the National Cyber Crime Portal  https://cybercrime.gov.in\n")
        r.write("- In many places in India you can also call the cyber fraud helpline  1930  where it is active\n\n")

        # Reminder
        r.write("## Reminder\n")
        r.write("This report is based on your answers and on the quick checks done in the clinic\n")
        r.write("It is meant to guide you and your family to take clear steps that reduce risk over time\n")
        r.write("Keep this page with your one page checklist and update both when your habits improve\n")

    print("Report saved in", out_file)

# --------------------------------------------------
# 7. Main flow
# --------------------------------------------------

def main():
    print("=== SAHAYAM clinic assistant  custom risk and report ===")
    print("This tool checks these areas")
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

    participant_code = ""
    while not participant_code:
        participant_code = input("Code for this person  for example P001  ").strip()
        if not participant_code:
            print("Please type a simple code like P001")

    participant_type = input("Type of participant  senior citizen or engineering student  ").strip().lower()
    age_group = input("Age group  for example 18 to 25 or 50 to 60 or 60 to 75  ").strip()
    language_raw = input("Language  english or telugu or hindi  ").strip()
    lang_code = normalise_language(language_raw)
    name = input("Name for checklist  you can also leave this empty  ").strip()
    phone_last4 = input("Last four digits of phone number  only for checklist print  ").strip()

    # Part 1
    print("\nPart 1  protections already on this phone and in accounts\n")
    mfa_before = yes_no_int("Is extra login protection like two step or otp already on for any important account")
    screen_before = yes_no_int("Is there already a lock on this phone such as pin pattern or fingerprint")
    bank_before = yes_no_int("Is there already a safe daily limit set in your banking or upi app")
    scam_before = score_int("Out of five sample sms or chat messages how many scams can you catch right now", 0, 5)

    # Part 2
    print("\nPart 2  wifi and network use\n")
    used_public_wifi = yes_no_int("In the last month have you connected this phone or laptop to public or free wifi in places like cafe station or mall")
    has_home_wifi_issues = yes_no_int("Does your home wifi still use a default or very simple password or an old router setting")

    # Part 3
    print("\nPart 3  qr code and payment habits\n")
    scanned_unknown_qr = yes_no_int("Have you scanned any qr code from posters papers or unknown forwards in chat")
    used_public_qr_payment = yes_no_int("Have you paid through qr without fully checking the name and amount on the payment screen")

    # Part 4
    print("\nPart 4  apps and updates\n")
    installed_unknown_apps = yes_no_int("Have you installed apps from outside the official store using files or links from others")
    os_out_of_date = yes_no_int("Are phone updates waiting for many weeks and not installed")

    # Part 5
    print("\nPart 5  usb devices and charging\n")
    inserted_unknown_usb = yes_no_int("Have you put pen drives or usb devices from other people into your laptop or pc")
    used_public_usb_charger = yes_no_int("Have you charged your phone from free public usb charging ports")

    # Part 6
    print("\nPart 6  sharing and passwords\n")
    shares_device_without_lock = yes_no_int("Do you give your phone to others while it is open or without any lock")
    password_reuse = yes_no_int("Do you use the same password for many sites or apps")
    has_password_manager = yes_no_int("Do you use a password manager app or service")

    # Part 7
    print("\nPart 7  scam messages and calls\n")
    fell_for_social_link_or_call = yes_no_int("Have you ever clicked a link or followed instructions in a call or chat about money kyc closure prize or refund and later felt it was suspicious")

    print("\nNow you run the teaching part for this person  phone settings sms and link demo qr demo password habits\n")
    input("When you finish teaching and changes are done press enter to continue  ")

    # After
    print("\nNow we note the state after your help\n")
    mfa_after = yes_no_int("Is extra login protection like two step or otp now enabled on at least one important account")
    screen_after = yes_no_int("Is a lock now set on this phone")
    bank_after = yes_no_int("Is a safe daily bank or upi limit now set or checked again")
    scam_after = score_int("Out of the same five example messages how many scams can you now catch", 0, 5)

    # Risk before and after
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

    # Checklist
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

    # Report
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
