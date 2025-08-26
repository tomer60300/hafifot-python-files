import os
from pathlib import Path
from typing import Generator


def walk_with_depth(root: Path, depth: int) -> Generator[Path, None, None]:
    """
    Yield files and dirs up to a given depth.
    depth = 0 -> only the root folder
    depth = 1 -> root + immediate files
    depth = 2 -> include subfolders, etc.
    depth = -1 -> unlimited
    """
    root = root.resolve()
    top_depth = len(root.parts)

    if depth == 0:
        yield root
        return

    for dirpath, dirnames, filenames in os.walk(root):
        current_depth = len(Path(dirpath).parts) - top_depth
        if depth != -1 and current_depth > depth:
            # too deep, skip
            dirnames[:] = []
            continue

        # yield folder itself
        yield Path(dirpath)

        # yield files inside
        for f in filenames:
            yield Path(dirpath) / f

        # prune dirs if max depth reached
        if depth != -1 and current_depth >= depth - 1:
            dirnames[:] = []  # don't go deeper