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
    max_size: Optional[int] = None
    archive_name: Optional[Path] = None
    archive_code: Optional[str] = None

    @classmethod
    def build(cls, folder: Path, depth: int, regex: str, max_size: Optional[int] = None,
              archive_name: Optional[Path] = None, archive_code: Optional[str] = None,
              ) -> Config:
        try:
            pattern = re.compile(regex)
        except re.error as exc:
            raise ArgsValidationError(f"invalid regex: {exc}") from exc

        return cls(folder=folder, depth=depth, pattern=pattern, max_size=max_size, archive_name=archive_name,
                   archive_code=archive_code, )

    def __post_init__(self) -> None:
        # folder
        if not isinstance(self.folder, Path) or not self.folder.is_dir() or self.folder.name=="":
            raise ArgsValidationError(f"{self.folder} is not an existing directory")
        # depth
        if not isinstance(self.depth, int) or self.depth < 1:
            raise ArgsValidationError("depth must be positive integer")
        # size
        if self.max_size is not None and (not isinstance(self.max_size, int) or  self.max_size < 0) :
            raise ArgsValidationError("max_size must be non-negative")
        # archive_path
        if self.archive_name is not None:
            parent = self.archive_name.parent or Path(".")
            if not parent.exists() or not parent.is_dir():
                raise ArgsValidationError(
                    f"path for archive '{self.archive_name}' does not exist or is not a directory"
                )
        # archive_code
        if self.archive_code is not None and not isinstance(self.archive_code, str):
            raise ArgsValidationError("archive_code must be a string")
        if self.archive_code and not self.archive_name:
            raise ArgsValidationError("archive_code given but --archive-path is missing")


def parse_args() -> Config:
    parser = ArgumentParser(prog="main.py", description="File finder tool")
    parser.add_argument("folder", type=Path, help="Folder path to search")
    parser.add_argument("depth", type=int, help="Search depth (1 ( immediate files, greater for sub-dirs)")
    parser.add_argument("regex", type=str, help="Regex pattern for filenames")
    parser.add_argument("--size", type=int, dest="max_size", default=None,
                        help="Minimum file size (bytes) to filter by")
    parser.add_argument("--archive_name", dest="archive_name", type=Path, default=None,
                        help="Enable archive result mode, give archive filename")
    args = parser.parse_args()
    return Config.build(**vars(args))
