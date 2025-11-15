"""
Helpers for SAHAYAM reports in simple language.
"""

def build_area_status(before_score, after_score, answers):
    """
    Decide a simple status per area: "ok", "watch", or "fix".
    """
    status = {}

    ok_phone = answers.get("screen_after", 0) == 1 and not answers.get("os_out_of_date", 0)
    status["Phone basics"] = "ok" if ok_phone else "watch"

    status["Extra login protection"] = "ok" if answers.get("mfa_after", 0) == 1 else "fix"
    status["Bank and UPI limits"] = "ok" if answers.get("bank_after", 0) == 1 else "fix"

    if answers.get("used_public_wifi", 0) or answers.get("has_home_wifi_issues", 0):
        status["WiFi and network use"] = "fix"
    else:
        status["WiFi and network use"] = "ok"

    if answers.get("used_public_qr_for_payment", 0) or answers.get("scanned_unknown_qr", 0):
        status["QR and payment habits"] = "fix"
    else:
        status["QR and payment habits"] = "ok"

    if answers.get("installed_unknown_apps", 0) or answers.get("os_out_of_date", 0):
        status["Apps and updates"] = "fix"
    else:
        status["Apps and updates"] = "ok"

    if answers.get("inserted_unknown_usb", 0) or answers.get("used_public_usb_charger", 0):
        status["USB and charging"] = "fix"
    else:
        status["USB and charging"] = "ok"

    if answers.get("password_reuse", 0) or answers.get("shares_device_without_lock", 0):
        status["Passwords and sharing"] = "fix"
    else:
        status["Passwords and sharing"] = "watch"

    scam_after = answers.get("scam_after", 0)
    if scam_after <= 2:
        status["Scam messages and calls"] = "fix"
    elif scam_after <= 3:
        status["Scam messages and calls"] = "watch"
    else:
        status["Scam messages and calls"] = "ok"

    return status

def snapshot_symbol(tag):
    if tag == "ok":
        return "✓"
    if tag == "watch":
        return "!"
    return "✗"

def build_ascii_snapshot(status_by_area, overall_cat_after):
    lines = []
    lines.append("Risk snapshot")
    lines.append("---------------------------")
    for area in [
        "Phone basics",
        "Extra login protection",
        "Bank and UPI limits",
        "WiFi and network use",
        "QR and payment habits",
        "Apps and updates",
        "USB and charging",
        "Passwords and sharing",
        "Scam messages and calls",
    ]:
        tag = status_by_area.get(area, "watch")
        sym = snapshot_symbol(tag)
        lines.append(f"{sym} {area}")
    lines.append("---------------------------")
    lines.append(f"Overall today: {overall_cat_after} risk")
    return lines

def build_top_actions(status_by_area, answers):
    actions = []

    if status_by_area.get("Bank and UPI limits") == "fix":
        actions.append("Set a daily bank or UPI limit that fits normal use and is not too high.")
    if status_by_area.get("Passwords and sharing") == "fix":
        actions.append("Change passwords on email and banking so they are not reused on other sites.")
    if status_by_area.get("WiFi and network use") == "fix":
        actions.append("Avoid banking on free public WiFi. Use mobile data or trusted home WiFi.")
    if status_by_area.get("QR and payment habits") == "fix":
        actions.append("Read the name and amount on every QR payment screen before you approve.")
    if status_by_area.get("Apps and updates") == "fix":
        actions.append("Remove unknown apps and run updates until nothing is pending.")
    if status_by_area.get("USB and charging") == "fix":
        actions.append("Stop using free USB charging points and unknown pen drives.")
    if status_by_area.get("Scam messages and calls") == "fix":
        actions.append("Slow down on messages or calls about money, KYC or prizes and use official apps.")

    return actions[:3]

# Old names kept so earlier imports do not break
def build_exposure_lines(*_, **__): return []
def build_protection_lines(*_, **__): return []
def build_section_phone_basic(*_, **__): return []
def build_section_wifi(*_, **__): return []
def build_section_qr(*_, **__): return []
def build_section_apps_and_updates(*_, **__): return []
def build_section_usb_and_charging(*_, **__): return []
def build_section_passwords(*_, **__): return []
def build_section_scams(*_, **__): return []
def build_next_steps_lines(*_, **__): return []
