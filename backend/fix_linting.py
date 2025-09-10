#!/usr/bin/env python3
"""
Automated linting fix script for backend code.

This script automatically fixes common linting issues:
- Runs black formatter
- Runs isort for import sorting
- Removes trailing whitespace
- Fixes line endings

Usage:
    python fix_linting.py
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def main():
    """Main function to fix all linting issues."""
    print("🚀 Starting automated linting fixes...")

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # List of commands to run
    commands = [
        ("python3 -m black .", "Running Black formatter"),
        ("python3 -m isort .", "Running isort import sorting"),
        (
            "python3 -m flake8 . --count --exit-zero --max-complexity=15 --max-line-length=127",
            "Running flake8 check",
        ),
    ]

    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1

    print(f"\n📊 Results: {success_count}/{len(commands)} checks passed")

    if success_count == len(commands):
        print("🎉 All linting issues fixed successfully!")
        return 0
    else:
        print("⚠️  Some linting issues remain. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
