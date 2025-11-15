import qrcode
from pathlib import Path

OUT_DIR = Path("qr_out")
OUT_DIR.mkdir(exist_ok=True, parents=True)

def make_qr(data: str, name: str):
    img = qrcode.make(data)
    path = OUT_DIR / name
    img.save(path)
    return path

def main():
    # Safe UPI-style string (example)
    safe = "upi://pay?pa=shop@okbank&pn=Local%20Grocery&am=250.00&tn=Groceries"
    # Fake string sending to attacker
    fake = "upi://pay?pa=fraud@okbank&pn=Refund%20Support&am=2500.00&tn=KYC%20Update"

    safe_path = make_qr(safe, "qr_safe_upi.png")
    fake_path = make_qr(fake, "qr_fake_upi.png")

    print("Generated QR codes in", OUT_DIR)
    print("  Safe payment example:", safe_path)
    print("  Fake payment example:", fake_path)
    print("Use them only for demos, never as real payment codes.")
    
if __name__ == "__main__":
    main()
