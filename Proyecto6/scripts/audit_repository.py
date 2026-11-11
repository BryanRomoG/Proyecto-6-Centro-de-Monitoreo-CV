"""Auditoría local de candidatos Git; no imprime valores de posibles secretos."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", ".cache"}


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def files_below(path: Path):
    for child in sorted(path.iterdir()):
        if child.name in SKIP or child.is_symlink():
            continue
        if child.is_dir():
            yield from files_below(child)
        elif child.is_file():
            yield child


def snapshot() -> dict:
    paths = []
    for i in range(1, 6):
        paths.extend(files_below(ROOT / f"Proyecto{i}"))
    paths.extend(files_below(ROOT / "Proyecto6/Docs"))
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}


def audit() -> dict:
    raw = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
    )
    candidates = sorted(set(raw.decode("utf-8").split("\0")) - {""})
    patterns = {
        "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
        "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
        "credential_in_url": re.compile(r"https?://[^\s/:]+:[^\s/@]+@"),
    }
    findings, large, private_names = [], [], []
    for relative in candidates:
        path = ROOT / relative
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > 20 * 1024 * 1024:
            large.append({"path": relative, "bytes": size})
        if path.name == ".env" or path.suffix.lower() in {".pem", ".key", ".sqlite", ".sqlite3"}:
            private_names.append(relative)
        if size > 2 * 1024 * 1024:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            for name, pattern in patterns.items():
                if pattern.search(line):
                    findings.append({"path": relative, "line": n, "rule": name})
    nested = []
    def find_git(folder):
        for item in folder.iterdir():
            if item.name == ".git":
                if item.parent != ROOT:
                    nested.append(item.relative_to(ROOT).as_posix())
            elif item.is_dir() and item.name not in SKIP and not item.is_symlink():
                find_git(item)
    find_git(ROOT)
    return {"candidate_files": len(candidates), "over_20_mib": large,
            "sensitive_names": private_names, "pattern_findings": findings,
            "nested_git": nested,
            "limits": "Escaneo heurístico, no certifica ausencia de información privada en imágenes o texto. Revisar selección antes de commit."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.baseline:
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(json.dumps(snapshot(), indent=2), encoding="utf-8")
        print("Snapshot de antecedentes y Docs conservado.")
        return
    report = audit()
    if args.compare:
        before = json.loads(args.compare.read_text(encoding="utf-8"))
        after = snapshot()
        report["changed_originals"] = sorted(k for k in before if before[k] != after.get(k))
        report["new_original_paths"] = sorted(set(after) - set(before))
    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
