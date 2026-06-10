import subprocess
import sys


def test_core_reproducibility_script_runs():
    proc = subprocess.run(
        [sys.executable, "code/reproduce_core_checks.py"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "Reviewer-ready checks passed" in proc.stdout
