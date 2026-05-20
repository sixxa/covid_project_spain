from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    scripts_dir = Path(__file__).resolve().parent
    scripts = sorted([p for p in scripts_dir.glob("[0-9][0-9]_*.py") if p.name != "00_fetch_data.py"])
    for script in scripts:
        print(f"Running {script.name}")
        subprocess.run([sys.executable, str(script)], check=True)
    print("All plot scripts completed.")


if __name__ == "__main__":
    main()
