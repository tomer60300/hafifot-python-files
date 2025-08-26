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
    pattern: re.Pattern

    @classmethod
    def build(cls, folder: Path, depth: int, regex: str) -> Config:
        logger = logging.getLogger(__name__)
        logger.debug(f"Validating CLI arguments:\n Path:{folder} -- Depth: {depth} -- Regex: {regex}")

        #Depth validation
        if depth < 1:
            logger.error("Invalid depth specified: %s", depth)
            raise ValueError("Depth must be 1 or greater")

        #Regex validation
        try:
            pattern = re.compile(regex)
        except re.error as exc:
            logger.error("Invalid regex pattern: %s (%s)", regex, exc)
            raise InvalidPatternError(f"Invalid regex: {exc}")

        # Folder validation
        if not folder.is_dir() or folder.root=="":
            logger.error("Invalid folder: %s (does not exist or is not a directory)", folder)
            raise ValueError(f"Folder {folder} does not exist or is not a directory")

        logger.debug("Validation successful")
        return cls(folder=folder, depth=depth, pattern=pattern)


def parse_args() -> Config:
    parser = ArgumentParser(prog="main.py", description="File finder tool")
    parser.add_argument("folder", type=Path, help="Folder path to search")
    parser.add_argument("depth", type=int, help="Search depth (1 ( immediate files, greater for sub-dirs)")
    parser.add_argument("regex", type=str, help="Regex pattern for filenames")
    args = parser.parse_args()
    return Config.build(**vars(args))
