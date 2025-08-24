import os
from pathlib import Path
from typing import Iterator
import re


def walk_with_depth(root: Path, depth: int,pattern: re.Pattern, max_size: int=0) -> Iterator[Path]:
    """
    Yield files and dirs up to a given depth.
    depth = 1 -> immediate files
    depth = 2 -> include subfolders, etc.
    max_size -> maximum file size in bytes ( equal included) ; 0 ignore sizes
    """
    root = root.resolve()
    top_depth = len(root.parts)

    for dirpath, dirnames, filenames in os.walk(root):
        current_depth = len(Path(dirpath).parts) - top_depth

        for file in filenames:
            file_path_obj =Path(dirpath) / file
            if max_size == 0:
                if pattern.match(file):
                    yield file_path_obj
            else:
                if pattern.match(file) and file_path_obj.stat().st_size<=max_size:
                    yield file_path_obj

        # prune dirs if max depth reached
        if current_depth >= depth - 1:
            dirnames.clear()  # don't go deeper
