import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "materials" / "generated"
OUT = ROOT / "materials" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)

def has_pandoc():
    try:
        subprocess.run(["pandoc", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def main():
    if not has_pandoc():
        print("pandoc is not installed.")
        print("On macOS you can install it with:")
        print("  brew install pandoc")
        print("After that, run this script again.")
        return

    reports = sorted(GEN.glob("report_*.en.md"))
    if not reports:
        print("No markdown reports found in", GEN)
        return

    for md in reports:
        pdf_name = md.with_suffix(".pdf").name
        pdf_path = OUT / pdf_name
        print("Converting", md.name, "->", pdf_name)
        subprocess.run(["pandoc", str(md), "-o", str(pdf_path)], check=True)

    print("Done. PDFs are in", OUT)

if __name__ == "__main__":
    main()
