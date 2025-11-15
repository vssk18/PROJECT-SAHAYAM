from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import subprocess

# Project paths
ROOT = Path(__file__).resolve().parents[2]
METRICS_CSV = ROOT / "metrics" / "baseline_vs_week1.csv"
GEN_DIR = ROOT / "materials" / "generated"


# -----------------------------
# Data model
# -----------------------------
@dataclass
class Answers:
    participant_type: str
    age_group: str
    language: str

    mfa_before: int
    mfa_after: int
    screen_before: int
    screen_after: int
    bank_before: int
    bank_after: int
    scam_before: int
    scam_after: int

    used_public_wifi: int
    has_home_wifi_issues: int
    scanned_unknown_qr: int
    used_public_qr_for_payment: int
    installed_unknown_apps: int
    os_out_of_date: int
    inserted_unknown_usb: int
    used_public_usb_charger: int
    shares_device_without_lock: int
    password_reuse: int
    has_password_manager: int
    fell_for_social_link_or_call: int


# -----------------------------
# Input helpers
# -----------------------------
def ask_yes_no(prompt: str) -> int:
    while True:
        ans = input(prompt + "  yes or no  ").strip().lower()
        if ans in ("y", "yes"):
            return 1
        if ans in ("n", "no"):
            return 0
        print("Please type yes or no")


def ask_int_0_5(prompt: str) -> int:
    while True:
        raw = input(prompt + "  number between 0 and 5  ").strip()
        try:
            val = int(raw)
        except ValueError:
            print("Please type a number from 0 to 5")
            continue
        if 0 <= val <= 5:
            return val
        print("Please type a number from 0 to 5")


# -----------------------------
# Risk scoring
# -----------------------------
def risk_score(a: Answers, use_after: bool) -> int:
    score = 0

    mfa = a.mfa_after if use_after else a.mfa_before
    screen = a.screen_after if use_after else a.screen_before
    bank = a.bank_after if use_after else a.bank_before
    scam = a.scam_after if use_after else a.scam_before

    if mfa == 0:
        score += 2
    if screen == 0:
        score += 2
    if bank == 0:
        score += 2
    score += max(0, 3 - scam)

    for flag in [
        a.used_public_wifi,
        a.has_home_wifi_issues,
        a.scanned_unknown_qr,
        a.used_public_qr_for_payment,
        a.installed_unknown_apps,
        a.os_out_of_date,
        a.inserted_unknown_usb,
        a.used_public_usb_charger,
        a.shares_device_without_lock,
        a.password_reuse,
        a.fell_for_social_link_or_call,
    ]:
        if flag:
            score += 1

    score = max(0, min(score, 10))
    return score


def risk_category(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


# -----------------------------
# Metrics file helpers
# -----------------------------
def next_code() -> str:
    if not METRICS_CSV.exists():
        return "P001"
    try:
        rows = METRICS_CSV.read_text(encoding="utf-8").strip().splitlines()
    except OSError:
        return "P001"
    if len(rows) <= 1:
        return "P001"
    last = rows[-1].split(",")[1]
    if last.startswith("P") and last[1:].isdigit():
        num = int(last[1:]) + 1
    else:
        num = 1
    return f"P{num:03d}"


def ensure_header():
    if METRICS_CSV.exists():
        return
    METRICS_CSV.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "session_id,participant_code,participant_type,age_group,language,"
        "mfa_before,mfa_after,screen_lock_before,screen_lock_after,"
        "bank_limit_before,bank_limit_after,scam_quiz_score_before,scam_quiz_score_after,"
        "used_public_wifi,has_home_wifi_issues,scanned_unknown_qr,used_public_qr_for_payment,"
        "installed_unknown_apps,os_out_of_date,inserted_unknown_usb,used_public_usb_charger,"
        "shares_device_without_lock,password_reuse,has_password_manager,fell_for_social_link_or_call,"
        "risk_score_before,risk_score_after,risk_category_before,risk_category_after,date,notes\n"
    )
    METRICS_CSV.write_text(header, encoding="utf-8")


def append_metrics(
    session_id: str,
    code: str,
    a: Answers,
    before: int,
    after: int,
    cat_before: str,
    cat_after: str,
    notes: str,
):
    ensure_header()
    row = [
        session_id,
        code,
        a.participant_type,
        a.age_group,
        a.language,
        str(a.mfa_before),
        str(a.mfa_after),
        str(a.screen_before),
        str(a.screen_after),
        str(a.bank_before),
        str(a.bank_after),
        str(a.scam_before),
        str(a.scam_after),
        str(a.used_public_wifi),
        str(a.has_home_wifi_issues),
        str(a.scanned_unknown_qr),
        str(a.used_public_qr_for_payment),
        str(a.installed_unknown_apps),
        str(a.os_out_of_date),
        str(a.inserted_unknown_usb),
        str(a.used_public_usb_charger),
        str(a.shares_device_without_lock),
        str(a.password_reuse),
        str(a.has_password_manager),
        str(a.fell_for_social_link_or_call),
        str(before),
        str(after),
        cat_before,
        cat_after,
        session_id,
        notes.replace(",", " "),
    ]
    with METRICS_CSV.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# -----------------------------
# Checklist + report
# -----------------------------
def run_checklist(name: str, phone_last4: str, participant_code: str):
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GEN_DIR / f"checklist_{participant_code}.en.md"
    cmd = [
        "python3",
        str(ROOT / "apps" / "py_checklist_generator" / "generate_checklist.py"),
        "--name",
        name or f"Participant {participant_code}",
        "--phone",
        "XXXX" + phone_last4,
        "--apps",
        "Google, WhatsApp, Bank",
        "--limit",
        "₹5,000",
        "--lang",
        "en",
        "--out",
        str(out_path),
    ]
    print("Creating one page checklist for this person")
    print("Running checklist generator")
    subprocess.run(cmd, check=True)
    print("Checklist saved in", out_path)


def generate_report(
    code: str,
    a: Answers,
    before: int,
    after: int,
    cat_before: str,
    cat_after: str,
    notes: str,
):
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    lines: list[str] = []

    lines.append(f"# SAHAYAM security report for {code}")
    lines.append("")
    lines.append(f"Date of this report: {today}")
    lines.append(f"Participant info: type: {a.participant_type}, age group: {a.age_group}")
    lines.append("")

    # Summary
    lines.append("## 1. Summary of this visit")
    delta = after - before
    if delta < 0:
        change_line = (
            f"- Change in this visit: risk reduced by {abs(delta)} points "
            "based on your answers and checks."
        )
    elif delta > 0:
        change_line = (
            f"- Change in this visit: risk increased by {delta} points "
            "based on your answers and checks."
        )
    else:
        change_line = "- Change in this visit: overall risk score stayed the same."
    lines.append(f"- Estimated risk before the clinic: {before} out of 10  (category: {cat_before})")
    lines.append(f"- Estimated risk after the clinic : {after} out of 10  (category: {cat_after})")
    lines.append(change_line)
    lines.append("")
    lines.append(
        "This score is not a guarantee or a formal audit. It is a guide built from your "
        "own answers and a few quick checks."
    )
    lines.append("")

    # Areas
    lines.append("## 2. Areas covered in this report")
    lines.append("- Phone basics such as lock screen and updates")
    lines.append("- Extra login protection such as two step verification")
    lines.append("- Banking and UPI daily limits")
    lines.append("- Public WiFi and home WiFi")
    lines.append("- QR code payments and random QR scans")
    lines.append("- Apps from outside the store and pending updates")
    lines.append("- USB devices and public USB charging")
    lines.append("- Password reuse, sharing and password managers")
    lines.append("- Scam messages, links and urgent calls")
    lines.append("")

    # Detailed sections
    lines.append("## 3. Detailed areas and next steps")
    lines.append("")

    # 3.1 Phone basics
    lines.append("### 3.1 Phone basics")
    if a.screen_after == 1:
        lines.append("- Your phone has a lock screen.")
    else:
        lines.append("- Your phone does not have a lock screen set.")
    if a.os_out_of_date:
        lines.append("- Some updates are still pending on this phone.")
    else:
        lines.append("- Updates are mostly current.")
    lines.append("**Recommended steps**")
    if a.screen_after == 0:
        lines.append("- Set a PIN, pattern or fingerprint lock on this phone.")
    if a.os_out_of_date:
        lines.append("- Connect to home WiFi and run system and app updates.")
    lines.append("")

    # 3.2 Extra login protection
    lines.append("### 3.2 Extra login protection")
    if a.mfa_after == 1:
        lines.append("- Extra login protection is on for at least one important account.")
    else:
        lines.append("- Extra login protection is still off for important accounts.")
    lines.append("**Recommended steps**")
    if a.mfa_after == 0:
        lines.append("- Turn on two step verification on your main email and banking app.")
    lines.append("- Never share one time codes with anyone, even if they say they are support.")
    lines.append("")

    # 3.3 Bank and UPI limits
    lines.append("### 3.3 Bank and UPI limits")
    if a.bank_after == 1:
        lines.append("- A daily bank or UPI limit is set or was checked in this session.")
    else:
        lines.append("- No clear daily limit is set inside your banking or UPI app.")
    lines.append("**Recommended steps**")
    lines.append("- Set a daily transfer limit that fits normal use but is not too high.")
    lines.append("- Use a lower limit for routine payments and confirm again for rare high value transfers.")
    lines.append("")

    # 3.4 WiFi and network use
    lines.append("### 3.4 WiFi and network use")
    if a.used_public_wifi:
        lines.append("- You used public or free WiFi recently.")
    if a.has_home_wifi_issues:
        lines.append("- Home WiFi may still have a simple password or old router settings.")
    lines.append("**Recommended steps**")
    if a.used_public_wifi:
        lines.append("- Avoid doing banking or very important changes on free public WiFi.")
    if a.has_home_wifi_issues:
        lines.append("- Change the router password to a longer one and use WPA2 or WPA3 if available.")
    lines.append("")

    # 3.5 QR codes and payments
    lines.append("### 3.5 QR codes and payments")
    if a.scanned_unknown_qr or a.used_public_qr_for_payment:
        lines.append("- You have used QR codes without always checking name and amount.")
    else:
        lines.append("- You already check QR payment details carefully.")
    lines.append("**Recommended steps**")
    lines.append("- Scan QR codes only from trusted shops or people.")
    lines.append("- Always read the name and amount on the payment confirmation screen before you tap approve.")
    lines.append("")

    # 3.6 Apps and updates
    lines.append("### 3.6 Apps and updates")
    if a.installed_unknown_apps:
        lines.append("- You installed apps from links or files outside the official store.")
    if a.os_out_of_date:
        lines.append("- There are still pending updates.")
    lines.append("**Recommended steps**")
    if a.installed_unknown_apps:
        lines.append("- Remove apps that you do not recognise or no longer use.")
    lines.append("- Keep phone and app updates running until nothing is pending.")
    lines.append("")

    # 3.7 USB devices and charging
    lines.append("### 3.7 USB devices and charging")
    if a.inserted_unknown_usb or a.used_public_usb_charger:
        lines.append("- You used unknown USB devices or free charging points.")
    else:
        lines.append("- You already avoid unsafe USB devices and charging points.")
    lines.append("**Recommended steps**")
    lines.append("- Prefer your own charger plugged into a normal power socket.")
    lines.append("- Avoid unknown pen drives and shared USB sticks.")
    lines.append("")

    # 3.8 Passwords and sharing
    lines.append("### 3.8 Passwords and sharing")
    if a.shares_device_without_lock:
        lines.append("- You sometimes give your phone to others while it is unlocked.")
    if a.password_reuse:
        lines.append("- The same password is reused on more than one site.")
    if a.has_password_manager:
        lines.append("- You already use a password manager.")
    lines.append("**Recommended steps**")
    if a.shares_device_without_lock:
        lines.append("- Lock the phone before handing it over or open only the app they need.")
    if a.password_reuse:
        lines.append("- Change passwords on email and banking so they are not reused elsewhere.")
    if not a.has_password_manager:
        lines.append("- Consider a simple password manager for your main accounts.")
    lines.append("")

    # 3.9 Scam messages and calls
    lines.append("### 3.9 Scam messages and calls")
    lines.append(f"- Scam quiz score before the clinic: {a.scam_before} out of 5.")
    lines.append(f"- Scam quiz score after the clinic : {a.scam_after} out of 5.")
    lines.append("**Recommended steps**")
    lines.append("- Slow down for calls or messages about urgent money, refunds, KYC or prizes.")
    lines.append("- Open official apps directly instead of using links from such messages.")
    lines.append("")

    # Help section
    lines.append("## 4. When to ask for help at once")
    lines.append("- If money moves without your clear action, call your bank helpline or the number shown in your official banking app.")
    lines.append("- If you shared a one time password, card number or PIN by mistake, call the bank and ask them to block and review.")
    lines.append("- For online fraud or suspicious links, you can raise a complaint on the National Cyber Crime Portal: https://cybercrime.gov.in")
    lines.append("- In many parts of India you can also call the cyber fraud helpline 1930 where it is active.")
    lines.append("")

    # Notes
    lines.append("## 5. Notes from this session")
    lines.append(notes or "")
    lines.append("")

    # Reminder
    lines.append("## 6. Reminder")
    lines.append("This report is based on one clinic visit and the answers you gave.")
    lines.append("Keep it with your one page checklist and update both as your habits improve.")

    out_path = GEN_DIR / f"report_{code}.en.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print("Report saved in", out_path)


# -----------------------------
# Main flow
# -----------------------------
def main():
    print("=== SAHAYAM clinic assistant  custom risk and report ===")
    print("This tool checks")
    print("1  screen lock and phone basics")
    print("2  extra login protection such as two step verification")
    print("3  bank and UPI daily limits")
    print("4  public WiFi and home WiFi")
    print("5  QR code payments and unknown QR codes")
    print("6  apps from outside the store and pending updates")
    print("7  USB devices and public USB charging")
    print("8  password reuse and password manager use")
    print("9  scam messages, links and urgent calls")
    print("")

    today = date.today().isoformat()
    session_id = input(f"Session id  press enter for {today}  ").strip() or today

    code = next_code()
    print("Generated code for this person ", code)

    participant_type = input("Type of participant  senior citizen or engineering student  ").strip() or "student"
    age_group = input("Age group  for example 18 to 25 or 50 to 60 or 60 to 75  ").strip()
    name = input("Name for checklist  you can also leave this empty  ").strip()
    phone_last4 = input("Last four digits of phone number  only for checklist print  ").strip()
    language = "en"

    print("")
    print("Part 1  protections already on this phone and in accounts")
    mfa_before = ask_yes_no("Is extra login protection like two step or OTP already on for any important account")
    screen_before = ask_yes_no("Is there already a lock on this phone such as PIN pattern or fingerprint")
    bank_before = ask_yes_no("Is there already a safe daily limit set in your banking or UPI app")
    scam_before = ask_int_0_5("Out of five sample SMS or chat messages how many scams can you catch right now")

    print("")
    print("Part 2  WiFi and network use")
    used_public_wifi = ask_yes_no("In the last month have you connected this phone or laptop to public or free WiFi such as cafe station or mall")
    has_home_wifi_issues = ask_yes_no("Does your home WiFi still use a default or very simple password or old router settings")

    print("")
    print("Part 3  QR code and payment habits")
    scanned_unknown_qr = ask_yes_no("Have you scanned any QR code from posters papers or unknown forwards in chat")
    used_public_qr_for_payment = ask_yes_no("Have you paid through QR without fully checking the name and amount on the screen")

    print("")
    print("Part 4  apps and updates")
    installed_unknown_apps = ask_yes_no("Have you installed apps from outside the official store using files or links from others")
    os_out_of_date = ask_yes_no("Are phone updates waiting for many weeks and not installed")

    print("")
    print("Part 5  USB devices and charging")
    inserted_unknown_usb = ask_yes_no("Have you put pen drives or USB devices from other people into your laptop or PC")
    used_public_usb_charger = ask_yes_no("Have you charged your phone from free public USB charging points")

    print("")
    print("Part 6  sharing and passwords")
    shares_device_without_lock = ask_yes_no("Do you give your phone to others while it is open or without any lock")
    password_reuse = ask_yes_no("Do you use the same password for many sites or apps")
    has_password_manager = ask_yes_no("Do you use a password manager app or service")

    print("")
    print("Part 7  scam messages and calls")
    fell_for_social_link_or_call = ask_yes_no("Have you ever clicked a link or followed instructions in a call or chat about money KYC closure prize or refund and later felt it was suspicious")

    # Build initial answers object (before changes)
    a_before = Answers(
        participant_type=participant_type,
        age_group=age_group,
        language=language,
        mfa_before=mfa_before,
        mfa_after=0,
        screen_before=screen_before,
        screen_after=0,
        bank_before=bank_before,
        bank_after=0,
        scam_before=scam_before,
        scam_after=0,
        used_public_wifi=used_public_wifi,
        has_home_wifi_issues=has_home_wifi_issues,
        scanned_unknown_qr=scanned_unknown_qr,
        used_public_qr_for_payment=used_public_qr_for_payment,
        installed_unknown_apps=installed_unknown_apps,
        os_out_of_date=os_out_of_date,
        inserted_unknown_usb=inserted_unknown_usb,
        used_public_usb_charger=used_public_usb_charger,
        shares_device_without_lock=shares_device_without_lock,
        password_reuse=password_reuse,
        has_password_manager=has_password_manager,
        fell_for_social_link_or_call=fell_for_social_link_or_call,
    )

    before = risk_score(a_before, use_after=False)
    cat_before = risk_category(before)

    print("")
    print("Now you run the teaching part for this person  phone settings SMS and link demo QR demo password habits")
    input("When you finish teaching and changes are done press enter to continue  ")

    print("")
    print("Now we note the state after your help")
    mfa_after = ask_yes_no("Is extra login protection like two step or OTP now enabled on at least one important account")
    screen_after = ask_yes_no("Is a lock now set on this phone")
    bank_after = ask_yes_no("Is a safe daily bank or UPI limit now set or checked again")
    scam_after = ask_int_0_5("Out of the same five example messages how many scams can you now catch")
    notes = input("Short notes about this session  optional  ").strip()

    # Final answers object (after changes)
    a_after = Answers(
        participant_type=participant_type,
        age_group=age_group,
        language=language,
        mfa_before=mfa_before,
        mfa_after=mfa_after,
        screen_before=screen_before,
        screen_after=screen_after,
        bank_before=bank_before,
        bank_after=bank_after,
        scam_before=scam_before,
        scam_after=scam_after,
        used_public_wifi=used_public_wifi,
        has_home_wifi_issues=has_home_wifi_issues,
        scanned_unknown_qr=scanned_unknown_qr,
        used_public_qr_for_payment=used_public_qr_for_payment,
        installed_unknown_apps=installed_unknown_apps,
        os_out_of_date=os_out_of_date,
        inserted_unknown_usb=inserted_unknown_usb,
        used_public_usb_charger=used_public_usb_charger,
        shares_device_without_lock=shares_device_without_lock,
        password_reuse=password_reuse,
        has_password_manager=has_password_manager,
        fell_for_social_link_or_call=fell_for_social_link_or_call,
    )

    after = risk_score(a_after, use_after=True)
    cat_after = risk_category(after)

    print(f"\nSaved metrics for {code}")
    print(f"Risk before   {before}  out of 10   {cat_before}")
    print(f"Risk after    {after}  out of 10   {cat_after}")

    append_metrics(session_id, code, a_after, before, after, cat_before, cat_after, notes)
    run_checklist(name, phone_last4, code)
    print("Creating detailed security report for this person")
    generate_report(code, a_after, before, after, cat_before, cat_after, notes)


if __name__ == "__main__":
    main()
