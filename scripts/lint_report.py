import os
import sys
import subprocess
from datetime import datetime


def main() -> int:
    targets = ["blueprints", "services", "app.py"]

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    txt_path = os.path.join(reports_dir, f"pylint-{ts}.txt")
    json_path = os.path.join(reports_dir, f"pylint-{ts}.json")

    base_cmd = [sys.executable, "-m", "pylint", *targets]

    print(f"Writing Pylint text report to: {txt_path}")
    with open(txt_path, "w", encoding="utf-8") as f:
        proc_txt = subprocess.run(base_cmd, stdout=f, stderr=subprocess.STDOUT)

    print(f"Writing Pylint JSON report to: {json_path}")
    with open(json_path, "w", encoding="utf-8") as f:
        proc_json = subprocess.run(base_cmd + ["-f", "json"], stdout=f, stderr=subprocess.STDOUT)

    latest_txt = os.path.join(reports_dir, "pylint-latest.txt")
    latest_json = os.path.join(reports_dir, "pylint-latest.json")
    try:
        for src, dst in ((txt_path, latest_txt), (json_path, latest_json)):
            if os.path.exists(dst):
                os.remove(dst)
            with open(src, "r", encoding="utf-8") as sf, open(dst, "w", encoding="utf-8") as df:
                df.write(sf.read())
    except Exception:
        pass

    rc = proc_txt.returncode or proc_json.returncode
    if rc != 0:
        print("Pylint found issues. See reports for details.")
    else:
        print("Pylint passed with configured rules.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

