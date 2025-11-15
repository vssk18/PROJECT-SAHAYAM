import subprocess
import sys
import datetime
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "metrics" / "baseline_vs_week1.csv"
GEN_DIR = ROOT / "materials" / "generated"

FIELDS = [
    "session_id","participant_code","participant_type","age_group","language",
    "mfa_before","mfa_after","screen_lock_before","screen_lock_after",
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

def compute_risk(mfa: int, screen: int, bank_limit: int, scam_score: int,
                 used_public_wifi: int, home_wifi_issues: int,
                 scanned_unknown_qr: int, used_public_qr_payment: int,
                 installed_unknown_apps: int, os_out_of_date: int,
                 inserted_unknown_usb: int, used_public_usb_charger: int,
                 shares_device_without_lock: int,
                 password_reuse: int, has_password_manager: int,
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
    score += home_wifi_issues * 2
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

def append_metrics(row: dict):
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = METRICS_PATH.exists() and METRICS_PATH.stat().st_size > 0
    with METRICS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def run_checklist_generator(name: str, phone_last4: str, language: str,
                            apps_str: str, limit: str, participant_code: str):
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out_file = GEN_DIR / f"checklist_{participant_code}.{language}.md"
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
    print("Running checklist generator")
    subprocess.run(cmd, check=True)
    print("Checklist saved in", out_file)

def generate_report(participant_code: str,
                    name: str,
                    language: str,
                    before_score: int,
                    after_score: int,
                    before_cat: str,
                    after_cat: str,
                    a: dict):
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out_file = GEN_DIR / f"report_{participant_code}.{language}.md"
    with out_file.open("w", encoding="utf-8") as r:
        r.write(f"# SAHAYAM security report for {participant_code}\n\n")
        if name:
            r.write(f"Name for clinic record  {name}\n\n")

        r.write(f"Risk before clinic  {before_score} out of 10   category  {before_cat}\n\n")
        r.write(f"Risk after clinic   {after_score} out of 10   category  {after_cat}\n\n")

        change = before_score - after_score
        if change > 0:
            r.write(f"You reduced your estimated risk by {change} points in this session\n\n")
        elif change == 0:
            r.write("Your estimated risk stayed the same in this session\n\n")
        else:
            r.write("Your estimated risk went up in this session  please read the advice with care\n\n")

        r.write("## Where your device and accounts are exposed\n")
        any_exposure = False
        if a["used_public_wifi"]:
            any_exposure = True
            r.write("- You used public or free wifi in the last month\n")
        if a["has_home_wifi_issues"]:
            any_exposure = True
            r.write("- Your home wifi may still have a weak or default password\n")
        if a["scanned_unknown_qr"]:
            any_exposure = True
            r.write("- You scanned qr codes from posters or forwards that you could not fully verify\n")
        if a["used_public_qr_for_payment"]:
            any_exposure = True
            r.write("- You used qr codes for payment without carefully checking the name and amount\n")
        if a["installed_unknown_apps"]:
            any_exposure = True
            r.write("- You installed apps from outside the official store\n")
        if a["os_out_of_date"]:
            any_exposure = True
            r.write("- Your phone or apps are waiting for updates for a long time\n")
        if a["inserted_unknown_usb"]:
            any_exposure = True
            r.write("- You plugged in usb drives or devices from people you do not fully trust\n")
        if a["used_public_usb_charger"]:
            any_exposure = True
            r.write("- You used public usb charging ports in places like malls or stations\n")
        if a["shares_device_without_lock"]:
            any_exposure = True
            r.write("- You give your phone to others while it is open without any lock\n")
        if a["password_reuse"]:
            any_exposure = True
            r.write("- You reuse the same password on many sites\n")
        if a["fell_for_social_link_or_call"]:
            any_exposure = True
            r.write("- You have clicked links or responded to calls or messages that felt urgent about money or kyc\n")

        if not any_exposure:
            r.write("- No major exposure was reported in this session\n")
        r.write("\n")

        r.write("## Protections you have or added today\n")
        if a["mfa_after"]:
            r.write("- You have multi factor protection on at least one important account\n")
        if a["screen_after"]:
            r.write("- Your phone now has a lock screen with pin pattern or fingerprint\n")
        if a["bank_after"]:
            r.write("- You set or checked a safe daily limit in your banking or upi app\n")
        if a["scam_after"] >= 4:
            r.write("- You can now catch at least four out of five scam messages in the small quiz\n")
        if a["has_password_manager"]:
            r.write("- You use a password manager which reduces password reuse\n")
        r.write("\n")

        r.write("## Advice based on your answers\n")

        if a["used_public_wifi"]:
            r.write("- Avoid banking and payments on public or open wifi  use mobile data or trusted wifi at home instead\n")
        if a["has_home_wifi_issues"]:
            r.write("- Change your wifi router password and set wifi security to wpa2 or wpa3 in the router settings\n")
        if a["scanned_unknown_qr"] or a["used_public_qr_for_payment"]:
            r.write("- Before paying with a qr code always check the name on the screen and the amount before you press pay\n")
            r.write("- Do not scan qr codes from random walls posters or unknown forwards on chat\n")
        if a["installed_unknown_apps"] or a["os_out_of_date"]:
            r.write("- Install only from official app stores and remove apps that you do not use or do not recognise\n")
            r.write("- Turn on automatic updates for your phone and key apps so that security fixes arrive on time\n")
        if a["inserted_unknown_usb"] or a["used_public_usb_charger"]:
            r.write("- Avoid using unknown usb drives in your laptop and avoid public usb charging ports when possible\n")
            r.write("- Prefer your own charger and a proper power socket\n")
        if a["shares_device_without_lock"]:
            r.write("- Keep a simple pin or pattern so that if someone takes your phone they cannot open apps freely\n")
        if a["password_reuse"]:
            r.write("- Use different passwords for email banking and social media  a password manager can help you remember them\n")
        if a["fell_for_social_link_or_call"]:
            r.write("- When a message or call talks about urgent kyc closure prize money or refund always stop and confirm with the bank or company using their official number or website\n")

        r.write("\n## Good habits for every person in the clinic\n")
        r.write("- Turn on multi factor protection on email banking and main social accounts\n")
        r.write("- Keep the phone and apps updated\n")
        r.write("- Never share otp pin or full card details with anyone on call or on chat\n")
        r.write("- Be careful with unknown links attachments and qr codes\n")
        r.write("- If you are unsure call a trusted family member or the bank before acting\n")

        r.write("\n## Where to ask for help in India\n")
        r.write("- National cyber crime portal  https://cybercrime.gov.in\n")
        r.write("- Cyber fraud helpline number  1930  where available\n")
        r.write("- For bank issues use the phone number printed on your bank card or printed on the passbook or official site\n")

    print("Report saved in", out_file)

def main():
    print("=== SAHAYAM clinic assistant  custom risk and report ===")
    today = datetime.date.today().isoformat()
    session_id = input(f"Session id  press enter for {today}  ").strip() or today
    participant_code = input("Participant code for this person  for example P001  ").strip()
    participant_type = input("Type of participant  senior citizen or engineering student  ").strip().lower()
    age_group = input("Age group  for example 18 to 25 or 50 to 60 or 60 to 75  ").strip()
    language = input("Language  english or telugu or hindi  ").strip().lower() or "english"
    name = input("Name for checklist  you can also leave this empty  ").strip()
    phone_last4 = input("Last four digits of phone number  only for checklist print  ").strip()

    print("\nNow we will note the current state before teaching\n")

    mfa_before = yes_no_int("Is extra login protection like two step or otp already on for any important account")
    screen_before = yes_no_int("Is there already a lock on this phone such as pin pattern or fingerprint")
    bank_before = yes_no_int("Is there already a safe daily limit set in your banking or upi app")
    scam_before = score_int("Out of five example sms or chat messages how many scams can you catch right now", 0, 5)

    used_public_wifi = yes_no_int("In the last month have you connected this phone or laptop to public or free wifi in places like cafe station or mall")
    has_home_wifi_issues = yes_no_int("Does your home wifi still use a default or simple password or a very old router setting")
    scanned_unknown_qr = yes_no_int("Have you scanned any qr code from posters papers or unknown forwards in chat")
    used_public_qr_payment = yes_no_int("Have you paid through qr without fully checking the name and amount on the screen")
    installed_unknown_apps = yes_no_int("Have you installed apps from outside the official store using files or links from others")
    os_out_of_date = yes_no_int("Are phone updates waiting for many weeks and not installed")
    inserted_unknown_usb = yes_no_int("Have you put pen drives or usb devices from other people into your laptop or pc")
    used_public_usb_charger = yes_no_int("Have you charged your phone from free public usb charging ports")
    shares_device_without_lock = yes_no_int("Do you give your phone to others while it is open or without any lock")
    password_reuse = yes_no_int("Do you use the same password for many sites or apps")
    has_password_manager = yes_no_int("Do you use a password manager app or service")
    fell_for_social_link_or_call = yes_no_int("Have you ever clicked a link or followed instructions in a call or chat that talked about money kyc closure prize or refund and felt suspicious later")

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
        0, 0, 0, 0, 0, 0,
        0, 0,
        shares_device_without_lock, password_reuse,
        has_password_manager, 0
    )

    cat_before = risk_category(before_score)
    cat_after = risk_category(after_score)

    today_str = today
    notes = input("Short notes about this session  optional  ").strip()

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
        language=language,
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
        language=language,
        before_score=before_score,
        after_score=after_score,
        before_cat=cat_before,
        after_cat=cat_after,
        a=answers
    )

    print("Clinic run complete for", participant_code)
    print("Checklist and report are stored in", GEN_DIR)

if __name__ == "__main__":
    main()
