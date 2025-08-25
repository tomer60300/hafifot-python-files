from __future__ import annotations
import re
from argparse import ArgumentParser, Namespace
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ArgsValidationError(TypeError, ValueError):
    """Raised when input arguments are invalid."""
    pass


@dataclass(frozen=True)
class Config:
    folder: Path
    depth: int
    pattern: re.Pattern
    size: int
    archive_name: str

    @classmethod
    def build(cls, folder: Path, depth: int, regex: str, size: int = 0, archive_name: str = None) -> Config:
        logger = logging.getLogger(__name__)
        logger.debug(f"Validating CLI arguments:\n Path:{folder} -- Depth: {depth} -- Regex: {regex}")

        cls._validate_folder(folder)
        cls._validate_depth(depth)
        cls._validate_size(size)
        cls._validate_archive_name(archive_name)
        pattern = cls._compile_regex(regex)

        logger.debug("Validation successful")
        return cls(folder=folder, depth=depth, pattern=pattern, size=size,archive_name=archive_name)

    @staticmethod
    def _validate_size(size: Optional[int]) -> None:
        if size is not None:
            if not isinstance(size, int):
                raise ArgsValidationError("size must be int")
            if size < 0:
                raise ArgsValidationError("size non negative")

    @staticmethod
    def _validate_depth(depth: int) -> None:
        if not isinstance(depth, int):
            raise ArgsValidationError("depth must be int")
        if depth < 1:
            raise ArgsValidationError("depth must be positive")

    @staticmethod
    def _validate_folder(folder: Path) -> None:
        if not isinstance(folder, Path):
            raise ArgsValidationError("folder must be pathlib.Path")
        if not folder.is_dir() or folder.root == "":
            raise ArgsValidationError(f"{folder} is not a directory")

    @staticmethod
    def _compile_regex(regex: str) -> re.Pattern:
        try:
            return re.compile(regex)
        except re.error as exc:
            raise ArgsValidationError(f"Invalid regex: {exc}")

    @staticmethod
    def _validate_archive_name(archive_name: str) -> None:
        INVALID_CHARS = r'<>:"/\\|?*'

        if not isinstance(archive_name, str):
            raise ArgsValidationError("Archive name must be string type")

        if any(ch in INVALID_CHARS for ch in archive_name):
            raise ArgsValidationError(f"Archive name can't be empty {archive_name}")


def parse_args() -> Config:
    parser = ArgumentParser(prog="main.py", description="File finder tool")
    parser.add_argument("folder", type=Path, help="Folder path to search")
    parser.add_argument("depth", type=int, help="Search depth (1 ( immediate files, greater for sub-dirs)")
    parser.add_argument("regex", type=str, help="Regex pattern for filenames")
    parser.add_argument("--size", type=int, default=0, help="Minimum file size (bytes) to filter by")
    parser.add_argument("--archive_name", type=str,default="", help="Enable archive result mode, give archive filename")
    args = parser.parse_args()
    return Config.build(**vars(args))
