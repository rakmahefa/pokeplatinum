#!/usr/bin/env python3
"""Emit a deterministic inventory of blobs in a committed Git tree.

Reads HEAD (or another explicitly selected commit), not the working directory.
Untracked/ignored files are excluded. LFS sizes refer to the pointer blob and
submodule contents are reported as gitlinks, not expanded files.
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional


def run_git(*args: str, input_bytes: Optional[bytes] = None) -> bytes:
    try:
        result = subprocess.run(
            ["git", *args],
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git was not found; install Git and run inside a repository") from exc
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError("git {} failed: {}".format(" ".join(args), message))
    return result.stdout


def extension_bucket(path: str) -> str:
    name = PurePosixPath(path).name
    if name.startswith(".") and name.count(".") == 1:
        return "[dotfile]"
    suffix = PurePosixPath(name).suffix.lower()
    return suffix if suffix else "[no extension]"


def load_inventory(revision: str, limit: int) -> Dict[str, Any]:
    resolved = run_git("rev-parse", "--verify", "{}^{{commit}}".format(revision)).decode().strip()
    tree_output = run_git("ls-tree", "-r", "-z", "--full-tree", resolved)

    blobs: List[Dict[str, str]] = []
    gitlinks: List[Dict[str, str]] = []
    symlinks: List[str] = []

    for record in tree_output.split(b"\0"):
        if not record:
            continue
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode, object_type, object_sha = metadata.decode("ascii").split()
        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError("could not parse a record returned by git ls-tree") from exc
        path = path_bytes.decode("utf-8", errors="surrogateescape")
        if object_type == "commit":
            gitlinks.append({"path": path, "commit": object_sha})
        elif object_type == "blob":
            blobs.append({"path": path, "sha": object_sha, "mode": mode})
            if mode == "120000":
                symlinks.append(path)

    sizes_by_sha: Dict[str, int] = {}
    unique_shas = sorted({entry["sha"] for entry in blobs})
    if unique_shas:
        batch_input = ("\n".join(unique_shas) + "\n").encode("ascii")
        batch_output = run_git(
            "cat-file",
            "--batch-check=%(objectname) %(objecttype) %(objectsize)",
            input_bytes=batch_input,
        )
        for line in batch_output.decode("ascii").splitlines():
            fields = line.split()
            if len(fields) != 3 or fields[1] != "blob":
                raise RuntimeError("unexpected response from git cat-file: {}".format(line))
            sizes_by_sha[fields[0]] = int(fields[2])
        missing = set(unique_shas) - set(sizes_by_sha)
        if missing:
            raise RuntimeError("git cat-file did not return sizes for {} blob(s)".format(len(missing)))

    by_top: Dict[str, Dict[str, int]] = defaultdict(lambda: {"files": 0, "blob_bytes": 0})
    by_extension: Dict[str, Dict[str, int]] = defaultdict(lambda: {"files": 0, "blob_bytes": 0})
    largest: List[Dict[str, Any]] = []
    total_bytes = 0

    for entry in blobs:
        path = entry["path"]
        size = sizes_by_sha[entry["sha"]]
        total_bytes += size
        top = path.split("/", 1)[0] if "/" in path else "[root]"
        ext = extension_bucket(path)
        by_top[top]["files"] += 1
        by_top[top]["blob_bytes"] += size
        by_extension[ext]["files"] += 1
        by_extension[ext]["blob_bytes"] += size
        largest.append({"path": path, "blob_bytes": size, "blob_sha": entry["sha"]})

    largest.sort(key=lambda item: (-item["blob_bytes"], item["path"]))
    gitlinks.sort(key=lambda item: item["path"])
    symlinks.sort()

    return {
        "schema_version": 1,
        "revision": resolved,
        "scope": (
            "committed Git tree only; excludes untracked/ignored working-tree files, "
            "expanded Git LFS objects and submodule contents"
        ),
        "summary": {
            "blob_files": len(blobs),
            "blob_bytes": total_bytes,
            "symlinks": len(symlinks),
            "gitlinks": len(gitlinks),
        },
        "by_top_level": {key: by_top[key] for key in sorted(by_top)},
        "by_extension": {key: by_extension[key] for key in sorted(by_extension)},
        "symlink_paths": symlinks,
        "gitlinks": gitlinks,
        "largest_files": largest[:limit],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="HEAD", help="commit or ref to inventory (default: HEAD)")
    parser.add_argument("--limit", type=int, default=30, help="number of largest blobs to report (default: 30)")
    parser.add_argument("--output", type=Path, help="write JSON to this path instead of stdout")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be non-negative")

    try:
        report = load_inventory(args.revision, args.limit)
    except RuntimeError as exc:
        print("repo_inventory: error: {}".format(exc), file=sys.stderr)
        return 2

    rendered = json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
