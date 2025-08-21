from __future__ import annotations
import re
from argparse import ArgumentParser, Namespace
import logging
from dataclasses import dataclass
from pathlib import Path


class InvalidPatternError(ValueError):
    """Raised when the regex pattern is invalid."""


@dataclass(frozen=True)
class Config:
    folder: Path
    depth: int
    pattern: str

    @classmethod
    def build_from_args(cls, args: Namespace) -> Config:
        logger = logging.getLogger(__name__)

        logger.debug("Validating CLI arguments: %s", args)

        # Depth validation
        if args.depth < 1:
            logger.error("Invalid depth specified: %s", args.depth)
            raise ValueError("Depth must be 1 or greater")

        # Regex validation
        try:
            re.compile(args.pattern)
        except re.error as exc:
            logger.error("Invalid regex pattern: %s (%s)", args.pattern, exc)
            raise InvalidPatternError(f"Invalid regex: {exc}")

        # Folder validation
        if not args.folder.is_dir() or args.folder.root=="":
            logger.error("Invalid folder: %s (does not exist or is not a directory)", args.folder)
            raise ValueError(f"Folder {args.folder} does not exist or is not a directory")

        logger.debug("Validation successful")
        return cls(folder=args.folder, depth=args.depth, pattern=args.pattern)


def parse_args() -> Config:
    parser = ArgumentParser(prog="main.py", description="File finder tool")
    parser.add_argument("folder", type=Path, help="Folder path to search")
    parser.add_argument("depth", type=int, help="Search depth (1 ( immediate files, greater for sub-dirs)")
    parser.add_argument("pattern", type=str, help="Regex pattern for filenames")
    args = parser.parse_args()
    return Config.build_from_args(args)
