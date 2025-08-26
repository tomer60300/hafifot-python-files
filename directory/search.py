import os
from pathlib import Path
from typing import Iterator
import re


def walk_with_depth(root: Path, depth: int,pattern: re.Pattern) -> Iterator[Path]:
    """
    Yield files and dirs up to a given depth.
    depth = 1 -> immediate files
    depth = 2 -> include subfolders, etc.
    """
    root = root.resolve()
    top_depth = len(root.parts)

    for dirpath, dirnames, filenames in os.walk(root):
        current_depth = len(Path(dirpath).parts) - top_depth

        for file in filenames:
            if pattern.match(file):
                yield Path(dirpath) / file

        # prune dirs if max depth reached
        if current_depth >= depth - 1:
            dirnames.clear()  # don't go deeper
