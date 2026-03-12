import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
IS_WINDOWS = os.name == "nt"


def venv_python_path() -> Path:
    if IS_WINDOWS:
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run_command(command, cwd=PROJECT_ROOT):
    subprocess.check_call(command, cwd=str(cwd))


def ensure_virtual_environment():
    if not VENV_DIR.exists():
        print("[setup] Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])


def ensure_requirements_installed():
    marker = VENV_DIR / ".deps_installed"
    requirements_file = PROJECT_ROOT / "requirements.txt"
    venv_python = str(venv_python_path())

    if not marker.exists() or marker.stat().st_mtime < requirements_file.stat().st_mtime:
        print("[setup] Installing dependencies...")
        run_command([venv_python, "-m", "pip", "install", "--upgrade", "pip"])
        run_command([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
        marker.write_text("Dependencies installed.\n", encoding="utf-8")


def ensure_instance_folder():
    (PROJECT_ROOT / "instance").mkdir(parents=True, exist_ok=True)


def start_app():
    venv_python = str(venv_python_path())
    print("[start] Running Inventory System at http://127.0.0.1:5000")
    run_command([venv_python, "run.py"])


def main():
    try:
        ensure_virtual_environment()
        ensure_requirements_installed()
        ensure_instance_folder()
        start_app()
    except subprocess.CalledProcessError as error:
        print(f"\n[error] Setup failed (exit code {error.returncode}).")
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()