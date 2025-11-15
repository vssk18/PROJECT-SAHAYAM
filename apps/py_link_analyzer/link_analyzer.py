import re
import argparse
from urllib.parse import urlparse

SUSPICIOUS_TLDS = {".cn", ".ru", ".top", ".work", ".click"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl"}

def analyze_url(url: str) -> dict:
    info = {"url": url, "score": 0, "reasons": []}
    try:
        parsed = urlparse(url if "://" in url else "http://" + url)
    except Exception:
        info["reasons"].append("parse_error")
        info["score"] += 1
        return info

    host = parsed.netloc.lower()

    # 1) IP address in host
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host.split(":")[0]):
        info["reasons"].append("ip_host")
        info["score"] += 2

    # 2) Suspicious TLD
    for t in SUSPICIOUS_TLDS:
        if host.endswith(t):
            info["reasons"].append(f"suspicious_tld({t})")
            info["score"] += 2
            break

    # 3) URL shorteners
    for s in SHORTENERS:
        if host == s or host.endswith("." + s):
            info["reasons"].append("shortener")
            info["score"] += 2
            break

    # 4) Excessive subdomains
    if host.count(".") >= 3:
        info["reasons"].append("many_subdomains")
        info["score"] += 1

    # 5) Bait words
    bait_words = ["support", "verify", "secure", "login", "update"]
    for w in bait_words:
        if w in host and not host.endswith(".google.com") and not host.endswith(".whatsapp.com"):
            info["reasons"].append(f"bait_word({w})")
            info["score"] += 1
            break

    return info

def main():
    ap = argparse.ArgumentParser(description="Offline URL risk analyzer for clinics.")
    ap.add_argument("file", help="Text file with one URL per line")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    total = len(urls)
    flagged = 0
    for u in urls:
        info = analyze_url(u)
        if info["score"] > 0:
            flagged += 1
            sev = "HIGH" if info["score"] >= 4 else "MEDIUM" if info["score"] >= 2 else "LOW"
            print(f"[{sev}] {u}  reasons={','.join(info['reasons'])}")
        else:
            print(f"[OK ] {u}")

    print(f"\nAnalyzed {total} URLs, flagged {flagged} as suspicious.")

if __name__ == "__main__":
    main()
