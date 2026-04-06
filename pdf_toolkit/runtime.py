from __future__ import annotations

import os
import pathlib
import site
import shutil
import subprocess
import sys
from collections.abc import Iterable, Sequence


def _normalize_candidates(paths: Iterable[pathlib.Path | str]) -> list[str]:
    candidates: list[str] = []
    seen: set[pathlib.Path] = set()
    for path in paths:
        candidate = pathlib.Path(path).expanduser()
        if not candidate.exists():
            continue
        absolute = candidate.absolute()
        if absolute in seen:
            continue
        seen.add(absolute)
        candidates.append(str(absolute))
    return candidates


def _module_probe(required_modules: Sequence[str]) -> str:
    imports = "\n".join(f"import {module}" for module in required_modules)
    return f"{imports}\n"


def interpreter_has_modules(
    python_executable: str, required_modules: Sequence[str]
) -> bool:
    result = subprocess.run(
        [python_executable, "-c", _module_probe(required_modules)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def discover_project_root(script_path: pathlib.Path | None = None) -> pathlib.Path:
    if script_path is None:
        script_path = pathlib.Path(__file__).resolve()

    current = script_path.resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / ".venv").exists() or (candidate / ".venv-watermark").exists():
            return candidate

    return current


def project_python_candidates(script_path: pathlib.Path | None = None) -> list[str]:
    if script_path is None:
        script_path = pathlib.Path(__file__).resolve()

    project_root = discover_project_root(script_path)
    local_envs = [
        project_root / ".venv" / "bin" / "python",
        project_root / ".venv-watermark" / "bin" / "python",
    ]

    command_paths = []
    for command_name in ("python", "python3"):
        candidate = shutil.which(command_name)
        if candidate:
            command_paths.append(candidate)

    return _normalize_candidates([sys.executable, *local_envs, *command_paths])


def bootstrap_local_site_packages(script_path: pathlib.Path | None = None) -> list[pathlib.Path]:
    project_root = discover_project_root(script_path)
    added_paths: list[pathlib.Path] = []

    for env_name in (".venv", ".venv-watermark"):
        lib_root = project_root / env_name / "lib"
        if not lib_root.exists():
            continue

        for site_packages in lib_root.glob("python*/site-packages"):
            site.addsitedir(str(site_packages))
            added_paths.append(site_packages)

    return added_paths


def maybe_reexec_with_modules(
    env_var: str,
    required_modules: Sequence[str],
    script_path: pathlib.Path | None = None,
    argv: Sequence[str] | None = None,
) -> None:
    if os.environ.get(env_var) == "1":
        return

    if interpreter_has_modules(sys.executable, required_modules):
        return

    if script_path is None:
        script_path = pathlib.Path(__file__).resolve()
    if argv is None:
        argv = sys.argv[1:]

    current_executable = pathlib.Path(sys.executable).absolute()
    for candidate in project_python_candidates(script_path):
        candidate_path = pathlib.Path(candidate).absolute()
        if candidate_path == current_executable:
            continue
        if not interpreter_has_modules(candidate, required_modules):
            continue

        env = os.environ.copy()
        env[env_var] = "1"
        os.execve(candidate, [candidate, str(script_path.resolve()), *argv], env)
