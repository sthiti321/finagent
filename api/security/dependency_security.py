import subprocess
import sys


def check_dependencies():
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip_audit",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            return {
                "status": "PASS",
                "vulnerabilities": [],
                "message": "No known vulnerabilities found in installed Python packages.",
            }

        return {
            "status": "FAIL",
            "vulnerabilities": result.stdout,
            "message": "One or more dependency vulnerabilities were detected.",
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL",
            "vulnerabilities": [],
            "message": "Dependency security scan timed out.",
        }

    except Exception as exc:
        return {
            "status": "FAIL",
            "vulnerabilities": [],
            "message": f"Dependency security scan failed: {str(exc)}",
        }