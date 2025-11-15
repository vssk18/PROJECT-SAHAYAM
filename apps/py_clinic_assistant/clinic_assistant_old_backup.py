from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "metrics" / "baseline_vs_week1.csv"
GEN_DIR = ROOT / "materials" / "generated"
CHECKLIST_SCRIPT = ROOT / "apps" / "py_checklist_generator" / "generate_checklist.py"


@dataclass
class Answers:
    session_id: str
    participant_code: str
    participant_type: str
    age_group: str
    language: str  # we use "en" now
    name: str
    phone_last4: str

    # before
    mfa_before: int
    screen_before: int
    bank_before: int
    scam_before: int

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

    # after
    mfa_after: int
    screen_after: int
    bank_after: int
    scam_after: int

    notes: str = ""


def ensure_dirs() -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)


def ask_yes_no(prompt: str) -> int:
    while True:
        ans = input(f"{prompt}  yes or no  ").strip().lower()
        if ans in {"yes", "y"}:
            return 1
        if ans in {"no", "n"}:
            return 0
        print("Please type yes or no")


def ask_int_in_range(prompt: str, lo: int, hi: int) -> int:
    while True:
        val = input(f"{prompt}  number between {lo} and {hi}  ").strip()
        try:
            n = int(val)
        except ValueError:
            print("Please type a number")
            continue
        if lo <= n <= hi:
            return n
        print(f"Please type a number from {lo} to {hi}")


def next_participant_code() -> str:
    """Look at existing metrics and pick the next P number."""
    if not METRICS_PATH.exists():
        return "P001"
    last = 0
    with METRICS_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("participant_code", "")
            if code.startswith("P") and len(code) >= 4 and code[1:4].isdigit():
                n = int(code[1:4])
                if n > last:
                    last = n
    return f"P{last+1:03d}" if last > 0 else "P001"


def compute_risk_score(a: Answers, before: bool = True) -> int:
    """Simple score 0 to 10."""
    if before:
        mfa = a.mfa_before
        screen = a.screen_before
        bank = a.bank_before
        scam = a.scam_before
    else:
        mfa = a.mfa_after
        screen = a.screen_after
        bank = a.bank_after
        scam = a.scam_after

    score = 0

    # missing protections
    if mfa == 0:
        score += 2
    if screen == 0:
        score += 1
    if bank == 0:
        score += 1

    risky_flags = [
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
    ]
    score += sum(1 for v in risky_flags if v == 1)

    # scam quiz, 0 safe side, low score means better
    score += max(0, 2 - scam)

    return max(0, min(10, score))


def risk_category(score: int) -> str:
    if score <= 3:
        return "low"
    if score <= 6:
        return "medium"
    return "high"


def write_metrics_row(a: Answers, before_score: int, after_score: int,
                      before_cat: str, after_cat: str) -> None:
    ensure_dirs()
    header = [
        "session_id",
        "participant_code",
        "participant_type",
        "age_group",
        "language",
        "mfa_before",
        "mfa_after",
        "screen_lock_before",
        "screen_lock_after",
        "bank_limit_before",
        "bank_limit_after",
        "scam_quiz_score_before",
        "scam_quiz_score_after",
        "used_public_wifi",
        "has_home_wifi_issues",
        "scanned_unknown_qr",
        "used_public_qr_for_payment",
        "installed_unknown_apps",
        "os_out_of_date",
        "inserted_unknown_usb",
        "used_public_usb_charger",
        "shares_device_without_lock",
        "password_reuse",
        "has_password_manager",
        "fell_for_social_link_or_call",
        "risk_score_before",
        "risk_score_after",
        "risk_category_before",
        "risk_category_after",
        "date",
        "notes",
    ]
    new_file = not METRICS_PATH.exists() or METRICS_PATH.stat().st_size == 0
    with METRICS_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "session_id": a.session_id,
            "participant_code": a.participant_code,
            "participant_type": a.participant_type,
            "age_group": a.age_group,
            "language": a.language,
            "mfa_before": a.mfa_before,
            "mfa_after": a.mfa_after,
            "screen_lock_before": a.screen_before,
            "screen_lock_after": a.screen_after,
            "bank_limit_before": a.bank_before,
            "bank_limit_after": a.bank_after,
            "scam_quiz_score_before": a.scam_before,
            "scam_quiz_score_after": a.scam_after,
            "used_public_wifi": a.used_public_wifi,
            "has_home_wifi_issues": a.has_home_wifi_issues,
            "scanned_unknown_qr": a.scanned_unknown_qr,
            "used_public_qr_for_payment": a.used_public_qr_for_payment,
            "installed_unknown_apps": a.installed_unknown_apps,
            "os_out_of_date": a.os_out_of_date,
            "inserted_unknown_usb": a.inserted_unknown_usb,
            "used_public_usb_charger": a.used_public_usb_charger,
            "shares_device_without_lock": a.shares_device_without_lock,
            "password_reuse": a.password_reuse,
            "has_password_manager": a.has_password_manager,
            "fell_for_social_link_or_call": a.fell_for_social_link_or_call,
            "risk_score_before": before_score,
            "risk_score_after": after_score,
            "risk_category_before": before_cat,
            "risk_category_after": after_cat,
            "date": a.session_id,
            "notes": a.notes,
        })
    print(f"Saved metrics for {a.participant_code}")


def run_checklist_generator(a: Answers) -> None:
    ensure_dirs()
    name = a.name or f"Participant {a.participant_code}"
    phone = "XXXX" + (a.phone_last4 or "0000")
    out_path = GEN_DIR / f"checklist_{a.participant_code}.en.md"
    cmd = [
        "python",
        str(CHECKLIST_SCRIPT),
        "--name", name,
        "--phone", phone,
        "--apps", "Google, WhatsApp, Bank",
        "--limit", "₹5,000",
        "--lang", "en",
        "--out", str(out_path),
    ]
    print("Creating one page checklist for this person")
    print("Running checklist generator")
    subprocess.run(cmd, check=True)
    print("Checklist saved in", out_path)


def _add_phone_basics_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.1 Phone basics")
    if a.screen_after == 1:
        lines.append("- Your phone has a lock screen.")
        lines.append("- This already blocks many casual attempts if the device is lost or shared.")
    else:
        lines.append("- Your phone does not have a lock screen set after this visit.")
        lines.append("- Anyone holding the phone can open apps and read messages.")
    if a.os_out_of_date:
        lines.append("- There are updates waiting and not installed.")
        lines.append("- Old versions often have known security problems.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    if a.screen_after == 0:
        lines.append("- Set a PIN, pattern or fingerprint lock and keep it on.")
    if a.os_out_of_date:
        lines.append("- Connect to trusted WiFi and install pending updates.")
    if not a.os_out_of_date and a.screen_after == 1:
        lines.append("- Keep the lock on and continue to install updates when the phone offers them.")


def _add_mfa_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.2 Extra login protection")
    if a.mfa_after == 1:
        lines.append("- Extra login protection such as two step verification is turned on for at least one important account.")
        lines.append("- A stolen password alone is usually not enough to enter that account.")
    else:
        lines.append("- Extra login protection is still off for your main accounts.")
        lines.append("- If someone learns a password they can sign in without a second check.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Turn on two step verification for email and banking if it is not already on.")
    lines.append("- Do not share one time codes with anyone, even if they say they are support.")


def _add_bank_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.3 Bank and UPI limits")
    if a.bank_after == 1:
        lines.append("- A safe daily limit is set or was checked again in this visit.")
        lines.append("- This can reduce the loss from a single mistake.")
    else:
        lines.append("- No clear daily limit is set or it was not checked.")
        lines.append("- Large transfers in one step remain possible if someone tricks you into approving them.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Open your bank or UPI app and set a daily transfer limit that fits normal life.")
    lines.append("- Use lower limits for routine payments and raise them only when truly needed.")


def _add_wifi_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.4 WiFi and network use")
    if a.used_public_wifi:
        lines.append("- You used public or free WiFi in the last month.")
        lines.append("- On open or weak WiFi someone on the same network may try to watch traffic or trick you with fake pages.")
    else:
        lines.append("- You did not use public or free WiFi often in the last month.")
    if a.has_home_wifi_issues:
        lines.append("- Your home WiFi seems to use a default or simple password or very old settings.")
        lines.append("- People nearby might guess a weak password and join your network.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Avoid opening banking and other important accounts on free public WiFi.")
    if a.has_home_wifi_issues:
        lines.append("- Change the WiFi router password so it does not contain your name, flat number or phone number.")
        lines.append("- Use WPA2 or WPA3 security mode and turn off WPS if the router has that setting.")


def _add_qr_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.5 QR codes and payments")
    if a.used_public_qr_for_payment or a.scanned_unknown_qr:
        lines.append("- You have used QR codes from posters, forwards or without full checks.")
        lines.append("- Fake QR codes can quietly change the receiver or the amount.")
    else:
        lines.append("- You mostly use QR codes from known shops or contacts.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Scan QR codes only from trusted shops or people.")
    lines.append("- Always read the name and amount on the payment screen before you tap approve.")


def _add_apps_updates_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.6 Apps and updates")
    if a.installed_unknown_apps:
        lines.append("- You have installed applications from links or files outside the official store.")
        lines.append("- Such apps can ask for wide permissions and may not be checked well.")
    else:
        lines.append("- You usually install apps from the official store.")
    if a.os_out_of_date:
        lines.append("- Phone or app updates are waiting and not installed.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Remove apps that you do not recognise or that you do not use anymore.")
    if a.os_out_of_date:
        lines.append("- Connect to trusted WiFi and run updates until nothing is pending.")


def _add_usb_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.7 USB devices and charging")
    if a.inserted_unknown_usb or a.used_public_usb_charger:
        lines.append("- You have used pen drives from others or free USB charging points.")
        lines.append("- Some devices can try to talk to your phone or laptop as a data device while charging.")
    else:
        lines.append("- You avoid unknown USB devices and free USB charging points.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Carry your own charger that plugs into a normal power socket.")
    lines.append("- Use only your own labelled USB drives where possible.")


def _add_passwords_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.8 Passwords and sharing")
    if a.shares_device_without_lock:
        lines.append("- You sometimes hand over your phone while it is unlocked.")
        lines.append("- In that state anyone can open apps, read codes and change settings.")
    if a.password_reuse:
        lines.append("- You reuse the same password on many sites.")
        lines.append("- If one site leaks the password, many other accounts can be taken over.")
    if a.has_password_manager:
        lines.append("- You use a password manager for at least some accounts.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Lock the phone before you hand it to someone and stay nearby if they use it.")
    lines.append("- Change passwords on your most important accounts so they are not shared with other sites.")
    if not a.has_password_manager:
        lines.append("- Consider starting with a simple password manager for email and banking.")


def _add_scam_section(lines, a: Answers, status: str) -> None:
    lines.append("### 4.9 Scam messages and calls")
    lines.append(f"- In the short quiz you spotted {a.scam_before} out of 5 scam messages before the clinic.")
    lines.append(f"- After the clinic you spotted {a.scam_after} out of 5.")
    lines.append("")
    lines.append("**Recommended steps for the coming week**")
    lines.append("- Slow down when a message or call talks about refunds, KYC, prizes or urgent payment.")
    lines.append("- Do not click links from such messages.")
    lines.append("- Open the official app directly or type the website address yourself.")
    lines.append("- Never share one time passwords or PINs with anyone.")


def _add_help_section(lines) -> None:
    lines.append("## 5. When to ask for help at once")
    lines.append("")
    lines.append("- If money moves without your clear action, call your bank helpline or the number in the official app.")
    lines.append("- If you shared a one time password, card number or PIN by mistake, call the bank and ask them to block and review.")
    lines.append("- For online fraud or suspicious messages and links you can raise a complaint on the National Cyber Crime Portal  https://cybercrime.gov.in")
    lines.append("- In many parts of India you can also call the cyber fraud helpline  1930 if it is active in your area.")


def generate_report(
    participant_code: str,
    name: str,
    lang_code: str,
    before_score: int,
    after_score: int,
    before_cat: str,
    after_cat: str,
    answers: dict,
):
    """Build a one page style report in simple English."""
    from risk_explanations import build_area_status, build_ascii_snapshot, build_top_actions

    ensure_dirs()
    today = date.today().isoformat()

    area_status = build_area_status(before_score, after_score, answers)
    snapshot_lines = build_ascii_snapshot(area_status, after_cat)
    top_actions = build_top_actions(area_status, answers)

    lines = []
    lines.append(f"# SAHAYAM security report for {participant_code}")
    lines.append("")
    lines.append(f"Date of this report: {today}")
    lines.append(
        f"Participant info: type: {answers.get('participant_type','')}, "
        f"age group: {answers.get('age_group','')}"
    )
    lines.append("")
    lines.append("```")
    lines.extend(snapshot_lines)
    lines.append("```")
    lines.append("")

    lines.append("## 1. Summary of this visit")
    delta = after_score - before_score
    if delta < 0:
        change_line = f"- Change in this visit  risk reduced by {abs(delta)} points based on your answers and checks."
    elif delta > 0:
        change_line = f"- Change in this visit  risk increased by {delta} points based on your answers and checks."
    else:
        change_line = "- Change in this visit  overall risk score stayed the same."
    lines.append(f"- Estimated risk before the clinic  {before_score} out of 10  category  {before_cat}")
    lines.append(f"- Estimated risk after the clinic   {after_score} out of 10  category  {after_cat}")
    lines.append(change_line)
    lines.append("")
    lines.append("This score is not a guarantee or a formal audit. It is a guide built from your own answers and a few quick checks.")
    lines.append("")

    lines.append("## 2. First three actions to focus on")
    if top_actions:
        for i, act in enumerate(top_actions, start=1):
            lines.append(f"{i}. {act}")
    else:
        lines.append("You already follow most of the strong habits we checked. Keep them steady.")
    lines.append("")

    lines.append("## 3. Areas covered in this report")
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

    lines.append("## 4. Detailed areas and next steps")
    lines.append("")
    _add_phone_basics_section(lines, answers, area_status.get("Phone basics", "watch"))
    lines.append("")
    _add_mfa_section(lines, answers, area_status.get("Extra login protection", "watch"))
    lines.append("")
    _add_bank_section(lines, answers, area_status.get("Bank and UPI limits", "watch"))
    lines.append("")
    _add_wifi_section(lines, answers, area_status.get("WiFi and network use", "watch"))
    lines.append("")
    _add_qr_section(lines, answers, area_status.get("QR and payment habits", "watch"))
    lines.append("")
    _add_apps_updates_section(lines, answers, area_status.get("Apps and updates", "watch"))
    lines.append("")
    _add_usb_section(lines, answers, area_status.get("USB and charging", "watch"))
    lines.append("")
    _add_passwords_section(lines, answers, area_status.get("Passwords and sharing", "watch"))
    lines.append("")
    _add_scam_section(lines, answers, area_status.get("Scam messages and calls", "watch"))
    lines.append("")
    _add_help_section(lines)
    lines.append("")
    lines.append("## 6. Notes from this session")
    note = answers.get("notes", "").strip()
    if note:
        lines.append(note)
    else:
        lines.append("No additional notes were recorded in this visit.")
    lines.append("")
    lines.append("## 7. Reminder")
    lines.append("This report is based on one clinic visit and the answers you gave.")
    lines.append("Keep it with your one page checklist and update both as your habits improve.")

    out_path = GEN_DIR / f"report_{participant_code}.en.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print("Report saved in", out_path)
    return out_path


def main():
    ensure_dirs()
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
    print()

    today = date.today().isoformat()
    session_id = input(f"Session id  press enter for {today}  ").strip() or today
    participant_code = next_participant_code()
    print("Generated code for this person ", participant_code)

    participant_type = input("Type of participant  senior citizen or engineering student  ").strip() or "student"
    age_group = input("Age group  for example 18 to 25 or 50 to 60 or 60 to 75  ").strip()
    name = input("Name for checklist  you can also leave this empty  ").strip()
    phone_last4 = input("Last four digits of phone number  only for checklist print  ").strip()[:4]

    print("\nPart 1  protections already on this phone and in accounts\n")
    mfa_before = ask_yes_no("Is extra login protection like two step or OTP already on for any important account")
    screen_before = ask_yes_no("Is there already a lock on this phone such as PIN pattern or fingerprint")
    bank_before = ask_yes_no("Is there already a safe daily limit set in your banking or UPI app")
    scam_before = ask_int_in_range("Out of five sample SMS or chat messages how many scams can you catch right now", 0, 5)

    print("\nPart 2  WiFi and network use\n")
    used_public_wifi = ask_yes_no("In the last month have you connected this phone or laptop to public or free WiFi such as cafe station or mall")
    has_home_wifi_issues = ask_yes_no("Does your home WiFi still use a default or very simple password or old router settings")

    print("\nPart 3  QR code and payment habits\n")
    scanned_unknown_qr = ask_yes_no("Have you scanned any QR code from posters papers or unknown forwards in chat")
    used_public_qr_for_payment = ask_yes_no("Have you paid through QR without fully checking the name and amount on the screen")

    print("\nPart 4  apps and updates\n")
    installed_unknown_apps = ask_yes_no("Have you installed apps from outside the official store using files or links from others")
    os_out_of_date = ask_yes_no("Are phone updates waiting for many weeks and not installed")

    print("\nPart 5  USB devices and charging\n")
    inserted_unknown_usb = ask_yes_no("Have you put pen drives or USB devices from other people into your laptop or PC")
    used_public_usb_charger = ask_yes_no("Have you charged your phone from free public USB charging points")

    print("\nPart 6  sharing and passwords\n")
    shares_device_without_lock = ask_yes_no("Do you give your phone to others while it is open or without any lock")
    password_reuse = ask_yes_no("Do you use the same password for many sites or apps")
    has_password_manager = ask_yes_no("Do you use a password manager app or service")

    print("\nPart 7  scam messages and calls\n")
    fell_for_social_link_or_call = ask_yes_no("Have you ever clicked a link or followed instructions in a call or chat about money KYC closure prize or refund and later felt it was suspicious")

    a = Answers(
        session_id=session_id,
        participant_code=participant_code,
        participant_type=participant_type,
        age_group=age_group,
        language="en",
        name=name,
        phone_last4=phone_last4,
        mfa_before=mfa_before,
        screen_before=screen_before,
        bank_before=bank_before,
        scam_before=scam_before,
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
        mfa_after=0,
        screen_after=0,
        bank_after=0,
        scam_after=0,
        notes="",
    )

    before_score = compute_risk_score(a, before=True)
    before_cat = risk_category(before_score)

    print()
    print("Now you run the teaching part for this person  phone settings SMS and link demo QR demo password habits")
    input("When you finish teaching and changes are done press enter to continue  ")
    print()
    print("Now we note the state after your help\n")

    a.mfa_after = ask_yes_no("Is extra login protection like two step or OTP now enabled on at least one important account")
    a.screen_after = ask_yes_no("Is a lock now set on this phone")
    a.bank_after = ask_yes_no("Is a safe daily bank or UPI limit now set or checked again")
    a.scam_after = ask_int_in_range("Out of the same five example messages how many scams can you now catch", 0, 5)
    a.notes = input("Short notes about this session  optional  ").strip()

    after_score = compute_risk_score(a, before=False)
    after_cat = risk_category(after_score)

    print()
    print(f"Risk before   {before_score}  out of 10   {before_cat}")
    print(f"Risk after    {after_score}  out of 10   {after_cat}")

    write_metrics_row(a, before_score, after_score, before_cat, after_cat)
    run_checklist_generator(a)

    answers_dict = {
        "participant_type": a.participant_type,
        "age_group": a.age_group,
        "mfa_before": a.mfa_before,
        "screen_before": a.screen_before,
        "bank_before": a.bank_before,
        "scam_before": a.scam_before,
        "mfa_after": a.mfa_after,
        "screen_after": a.screen_after,
        "bank_after": a.bank_after,
        "scam_after": a.scam_after,
        "used_public_wifi": a.used_public_wifi,
        "has_home_wifi_issues": a.has_home_wifi_issues,
        "scanned_unknown_qr": a.scanned_unknown_qr,
        "used_public_qr_for_payment": a.used_public_qr_for_payment,
        "installed_unknown_apps": a.installed_unknown_apps,
        "os_out_of_date": a.os_out_of_date,
        "inserted_unknown_usb": a.inserted_unknown_usb,
        "used_public_usb_charger": a.used_public_usb_charger,
        "shares_device_without_lock": a.shares_device_without_lock,
        "password_reuse": a.password_reuse,
        "has_password_manager": a.has_password_manager,
        "fell_for_social_link_or_call": a.fell_for_social_link_or_call,
        "notes": a.notes,
    }

    print("Creating detailed security report for this person")
    generate_report(
        participant_code=a.participant_code,
        name=a.name,
        lang_code=a.language,
        before_score=before_score,
        after_score=after_score,
        before_cat=before_cat,
        after_cat=after_cat,
        answers=answers_dict,
    )
    print("Clinic run complete for", a.participant_code)
    print("Checklist and report are stored in", GEN_DIR)


if __name__ == "__main__":
    main()
