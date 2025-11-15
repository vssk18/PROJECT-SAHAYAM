import subprocess
import sys
from pathlib import Path

# Point to project root (project-sahayam folder)
ROOT = Path(__file__).resolve().parents[2]

def run(cmd, cwd=None):
    """Run a command and show what is happening."""
    print("\n>>>", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None)

def show_menu():
    print("\nSAHAYAM assistant")
    print("-----------------")
    print("1) Run a new clinic session")
    print("2) Show current metrics summary")
    print("3) List available security reports")
    print("4) Exit")
    choice = input("Choose an option (1-4): ").strip()
    return choice

def list_reports():
    gen = ROOT / "materials" / "generated"
    if not gen.exists():
        print("\nNo reports have been generated yet.")
        return

    reports = sorted(gen.glob("report_*.en.md"))
    if not reports:
        print("\nNo reports have been generated yet.")
        return

    print("\nReports in materials/generated:\n")
    for p in reports:
        print("-", p.name)
    print("\n(You can open these files in any text editor.)")

def main():
    while True:
        choice = show_menu()

        if choice == "1":
            run(
                [sys.executable, "clinic_assistant.py"],
                cwd=ROOT / "apps" / "py_clinic_assistant"
            )

        elif choice == "2":
            run(
                [sys.executable, "summarize_metrics.py"],
                cwd=ROOT / "apps" / "py_metrics_logger"
            )

        elif choice == "3":
            list_reports()

        elif choice == "4":
            print("Closing SAHAYAM assistant.")
            break

        else:
            print("Please type a number between 1 and 4.")

if __name__ == "__main__":
    main()
