import csv
from pathlib import Path
from statistics import mean

METRICS_PATH = Path(__file__).resolve().parents[2] / "metrics" / "baseline_vs_week1.csv"

def load_rows():
    if not METRICS_PATH.exists():
        print("No metrics file found at", METRICS_PATH)
        return []
    with METRICS_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def to_int(row, key):
    try:
        return int(row[key])
    except Exception:
        return 0

def main():
    print("=== SAHAYAM metrics summary ===")
    print("File:", METRICS_PATH)
    rows = load_rows()
    if not rows:
        print("No data yet.")
        return

    total = len(rows)
    print("Total participants logged:", total)

    mfa_gain = []
    screen_gain = []
    bank_gain = []
    scam_gain = []

    for r in rows:
        mfa_before = to_int(r, "mfa_before")
        mfa_after = to_int(r, "mfa_after")
        screen_before = to_int(r, "screenlock_before")
        screen_after = to_int(r, "screenlock_after")
        bank_before = to_int(r, "banklimit_before")
        bank_after = to_int(r, "banklimit_after")
        scam_before = to_int(r, "scam_score_before")
        scam_after = to_int(r, "scam_score_after")

        mfa_gain.append(mfa_after - mfa_before)
        screen_gain.append(screen_after - screen_before)
        bank_gain.append(bank_after - bank_before)
        scam_gain.append(scam_after - scam_before)

    def pct_enabled(gains):
        # how many went from 0 -> 1
        improved = sum(1 for g in gains if g == 1)
        return 100.0 * improved / total

    print(f"MFA adoption (0->1): {pct_enabled(mfa_gain):.1f}% of participants")
    print(f"Screen lock adoption (0->1): {pct_enabled(screen_gain):.1f}% of participants")
    print(f"Bank limit adoption (0->1): {pct_enabled(bank_gain):.1f}% of participants")

    print(f"Average scam-score improvement (out of 5): {mean(scam_gain):.2f}")

if __name__ == "__main__":
    main()
