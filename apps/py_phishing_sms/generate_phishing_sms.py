import random
import datetime

CATEGORIES = {
    "bank_kyc": [
        "Dear customer, your bank KYC will be blocked today. Click {link} to update now.",
        "Important: your account is on hold due to incomplete KYC. Verify here: {link}",
        "Alert: KYC verification pending. Your card may be blocked. Visit {link}."
    ],
    "upi": [
        "You have received a refund of ₹{amount}. Approve within 30 minutes: {link}",
        "₹{amount} cashback is waiting in your UPI wallet. Tap {link} to claim.",
        "Your UPI ID will be deactivated. Confirm to keep it active: {link}"
    ],
    "courier": [
        "Your parcel is waiting at the hub. Pay ₹{amount} service charge at {link}.",
        "Delivery failed due to wrong address. Reschedule delivery at {link}.",
        "Customs duty of ₹{amount} pending for your parcel. Pay now: {link}."
    ],
    "electricity": [
        "Electricity bill overdue. Power will be cut tonight. Pay immediately at {link}.",
        "Your electricity meter will be disconnected due to non payment. Check bill at {link}.",
        "Last warning for power cut notice. Clear dues here: {link}."
    ],
    "job_prize": [
        "You have been shortlisted for a work from home job. Register here: {link}.",
        "You have won a lucky draw of ₹{amount}. Claim here: {link}.",
        "Instant loan pre approved up to ₹{amount}. Apply in 2 minutes at {link}."
    ]
}

SHORT_LINKS = [
    "bit.ly/verify-{n}",
    "tinyurl.com/refund-{n}",
    "is.gd/pay-{n}",
    "rb.gy/kyc-{n}"
]

def random_amount():
    return random.choice(["499", "999", "2,499", "4,999", "7,500"])

def random_link():
    base = random.choice(SHORT_LINKS)
    return "https://" + base.format(n=random.randint(100, 999))

def generate_message(category):
    template = random.choice(CATEGORIES[category])
    return template.format(amount=random_amount(), link=random_link())

def generate_set(n=20):
    out = []
    today = datetime.date.today().isoformat()
    for _ in range(n):
        cat = random.choice(list(CATEGORIES.keys()))
        msg = generate_message(cat)
        out.append((today, cat, msg))
    return out

def main():
    msgs = generate_set(20)
    print("# Sample suspicious SMS set")
    print("# date, category, message\n")
    for d, cat, msg in msgs:
        print(f"[{d}] [{cat}] {msg}")

if __name__ == "__main__":
    main()
