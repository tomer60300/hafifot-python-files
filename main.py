from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
import re

class InvalidPatternError(ValueError):
    pass

@dataclass(frozen=True)
class Config:
    folder: Path
    depth: int
    pattern: str

    @classmethod
    def from_namespace(cls, ns: argparse.Namespace) -> "Config":
        # Validation here
        if ns.depth < -1:
            raise ValueError("Depth must be -1 (unlimited) or >= 0")
        try:
            re.compile(ns.pattern)
        except re.error as exc:
            raise InvalidPatternError(f"Invalid regex: {exc}")
        if not ns.folder.is_dir():
            raise ValueError(f"Folder {ns.folder} does not exist or is not a directory")
        return cls(folder=ns.folder, depth=ns.depth, pattern=ns.pattern)

def parse_args() -> Config:
    parser = argparse.ArgumentParser(prog="files.py", description="File finder tool")
    parser.add_argument("folder", type=Path, help="Folder path to search")
    parser.add_argument("depth", type=int, help="Search depth (-1 unlimited)")
    parser.add_argument("pattern", type=str, help="Regex pattern for filenames")
    ns = parser.parse_args()
    return Config.from_namespace(ns)

if __name__ == "__main__":
    config = parse_args()
    print(config)
