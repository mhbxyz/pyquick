from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _repo_src() -> Path:
    return _repo_root() / "src"


def _env_with_repo_src() -> dict[str, str]:
    env = dict(os.environ)
    previous = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{_repo_src()}:{previous}" if previous else str(_repo_src())
    return env


def _run_pyqck(args: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pyqck", *args],
        cwd=cwd,
        env=_env_with_repo_src(),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def test_e2e_lib_workflow_new_install_test_check(tmp_path: Path) -> None:
    create = _run_pyqck(["new", "mylib", "--profile", "lib"], cwd=tmp_path)
    assert create.returncode == 0, create.stdout + create.stderr

    project_dir = tmp_path / "mylib"

    install = _run_pyqck(["install"], cwd=project_dir, timeout=240)
    assert install.returncode == 0, install.stdout + install.stderr

    test_result = _run_pyqck(["test"], cwd=project_dir)
    assert test_result.returncode == 0, test_result.stdout + test_result.stderr

    check_result = _run_pyqck(["check"], cwd=project_dir)
    assert check_result.returncode == 0, check_result.stdout + check_result.stderr
