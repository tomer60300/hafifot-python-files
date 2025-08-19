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
    def build_from_args(cls, args: argparse.Namespace) -> "Config":
        # Validation here
        if args.depth < 0:
            raise ValueError("Depth must be -1 (unlimited) or >= 0")
        try:
            re.compile(args.pattern)
        except re.error as exc:
            raise InvalidPatternError(f"Invalid regex: {exc}")
        if not args.folder.is_dir():
            raise ValueError(f"Folder {args.folder} does not exist or is not a directory")
        return cls(folder=args.folder, depth=args.depth, pattern=args.pattern)

def parse_args() -> Config:
    parser = argparse.ArgumentParser(prog="main.py", description="File finder tool")
    parser.add_argument("folder", type=Path, help="Folder path to search")
    parser.add_argument("depth", type=int, help="Search depth (-1 unlimited)")
    parser.add_argument("pattern", type=str, help="Regex pattern for filenames")
    args = parser.parse_args()
    return Config.build_from_args(args)

if __name__ == "__main__":
    config = parse_args() 
    print(config)
