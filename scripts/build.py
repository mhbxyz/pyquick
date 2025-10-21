#!/usr/bin/env python3
"""Build script for creating binary distributions of Anvil."""

import platform
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return True if successful."""
    try:
        subprocess.run(
            cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False


def build_binary():
    """Build standalone binary using PyInstaller."""
    print("Building binary with PyInstaller...")

    # Create dist directory if it doesn't exist
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)

    # Determine platform-specific binary name
    system = platform.system().lower()

    if system == "windows":
        binary_name = "anvil.exe"
    else:
        binary_name = "anvil"

    # PyInstaller command
    cmd = [
        "uv",
        "run",
        "pyinstaller",
        "--onefile",  # Create single executable
        "--name",
        "anvil",
        "--distpath",
        str(dist_dir),
        "--workpath",
        "build",
        "--specpath",
        "build",
        "--clean",  # Clean cache
        "--noconfirm",  # Don't ask for confirmation
        # Entry point
        "src/anvil/cli.py",
    ]

    if run_command(" ".join(cmd)):
        binary_path = dist_dir / binary_name
        if binary_path.exists():
            size = binary_path.stat().st_size
            print(f"✅ Binary built successfully: {binary_path} ({size} bytes)")
            return True
        else:
            print("❌ Binary not found after build")
            return False
    else:
        print("❌ Binary build failed")
        return False


def build_wheel():
    """Build wheel distribution."""
    print("Building wheel distribution...")
    return run_command("uv build --wheel")


def build_sdist():
    """Build source distribution."""
    print("Building source distribution...")
    return run_command("uv build --sdist")


def main():
    """Main build function."""
    print("🚀 Building Anvil distributions...")

    # Ensure we're in the project root
    if not Path("pyproject.toml").exists():
        print("❌ Not in project root (pyproject.toml not found)")
        sys.exit(1)

    # Install build dependencies
    print("Installing build dependencies...")
    if not run_command("uv sync"):
        print("❌ Failed to install dependencies")
        sys.exit(1)

    success = True

    # Build wheel
    if not build_wheel():
        success = False

    # Build source distribution
    if not build_sdist():
        success = False

    # Build binary
    if not build_binary():
        success = False

    if success:
        print("✅ All builds completed successfully!")
        print("\n📦 Distributions created in dist/:")
        for item in Path("dist").iterdir():
            if item.is_file():
                size = item.stat().st_size
                print(f"  - {item.name} ({size} bytes)")
    else:
        print("❌ Some builds failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
