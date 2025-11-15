import csv
import random
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[2] / "metrics" / "synthetic_sahayam_dataset.csv"

first_names = ["Arjun","Priya","Ravi","Ananya","Vikas","Deepa","Suresh","Kavita","Manoj","Geeta","Rajesh","Sunita","Amit","Nisha","Vijay","Leela","Rahul","Meera","Sanjay","Radhika"]
last_names = ["Sharma","Reddy","Patel","Singh","Kumar","Joshi","Iyer","Chowdhury","Gupta","Nath","Das","Mehta","Verma","Chakraborty","Bhat","Naidu"]

participant_types = ["senior citizen","engineering student"]
ages_students = ["18-25","26-30","31-35"]
ages_seniors = ["50-60","61-70","71-80"]

FIELDS = ["participant_code","participant_type","age_group","language",
          "mfa_before","mfa_after","screen_lock_before","screen_lock_after",
          "bank_limit_before","bank_limit_after","scam_quiz_score_before","scam_quiz_score_after",
          "used_public_wifi","scanned_unknown_qr","inserted_unknown_usb","fell_for_social_link",
          "risk_score_before","risk_score_after"]

rows = []
count = 0
for i in range(300):
    count += 1
    participant_code = f"P{1000 + count}"
    if i < 12:
        ptype = "senior citizen"
        age = random.choice(ages_seniors)
    else:
        ptype = "engineering student"
        age = random.choice(ages_students)
    lang = random.choice(["english","telugu","hindi"])
    # simulate before state
    mfa_b = random.choice([0,1] if ptype=="engineering student" else [0,0,1])
    screen_b = random.choice([1] if ptype=="engineering student" else [0,0,1])
    bank_b = random.choice([0,1])
    scam_b = random.randint(0,2) if ptype=="senior citizen" else random.randint(1,3)
    wifi_r = random.choice([0,1])
    qr_r = random.choice([0,1])
    usb_r = random.choice([0,1])
    social_r = random.choice([0,1])
    # after state simulate improvement for seniors
    mfa_a = 1 if random.random() < 0.7 else mfa_b
    screen_a = 1 if random.random() < 0.65 else screen_b
    bank_a = 1 if random.random() < 0.6 else bank_b
    scam_a = min(5, scam_b + random.randint(1,3))
    risk_b = 10 - (3*mfa_b + 2*screen_b + 2*bank_b) + wifi_r + qr_r + usb_r + social_r
    risk_a = max(0, 10 - (3*mfa_a + 2*screen_a + 2*bank_a))
    rows.append([participant_code,ptype,age,lang,mfa_b,mfa_a,screen_b,screen_a,bank_b,bank_a,scam_b,scam_a,wifi_r,qr_r,usb_r,social_r,risk_b,risk_a])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(FIELDS)
    writer.writerows(rows)
print("Synthetic dataset generated at", OUTPUT)
