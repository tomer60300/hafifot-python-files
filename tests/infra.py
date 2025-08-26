import re
from argparse import Namespace

from pytest import param, fixture
from pathlib import Path
from operations.operation import Mode
from typing import Set

MATCH_ALL_PATTERN = re.compile(r".*")

REGEXES = [
    param(r".*", id="match-all"),
    param(r".*\.txt", id="match-txt-files"),
    param(r"^C:\\Users\\[A-Za-z0-9_]+\\Documents\\.*", id="match-windows-document-path"),
]
ARCHIVE_CASES = [
    param(None, None, id="no-archive"),
    param(Path("archive.zip"), None, id="archive-no-code"),
    param(Path("archive.zip"), "1a2b3c", id="archive-code-mixed-int-str"),
    param(Path("archive.zip"), "1@a!^", id="archive-code-specials-chars"),
]

SIZES = [
    param(None, id="size-none"),
    param(0, id="size-0"),
    param(1024, id="size-1KB"),
    param(10 * 1024 * 1024, id="size-10MB"),
]

DEPTHS = [
    param(1, id="depth-1"),
    param(2, id="depth-2"),
]

FS_MOCK_TEMPLATE = [
    "root.txt",
    "logo.png",
    "docs/readme.txt",
    "docs/guide.md",
    "docs/specs/api.txt",
    "docs/specs/schema.json",
    "docs/images/diagram.png",
    "src/main.py",
    "src/utils.py",
    "src/assets/icon.png",
    "src/assets/banner.jpg",
    "src/templates/base.html",
    "data/raw/input.csv",
    "data/raw/notes.txt",
    "data/processed/output.csv",
    "tests/test_main.py",
    "tests/fixtures/sample.txt",
    "binaries/tool.bin",
    "binaries/win/app.exe",
    "logs/",  # empty folder
    "tmp/emptydir/",  # empty folder
]


NO_FILTER_MODE = Mode(size_filter=False,archive_filter=False,archive_lock_filter=False)
SIZE_FILTER_MODE = Mode(size_filter=True,archive_filter=False,archive_lock_filter=False)
ARCHIVE_FILTER_MODE = Mode(archive_filter=True,archive_lock_filter=False,size_filter=False)
LOCK_FILTER_MODE = Mode(archive_filter=True,archive_lock_filter=True,size_filter=False)

SUB_SUB_DIR_DEPTH = 3

def create_fs_from_template(root_path: Path):
    """
    Create files and directories from a flat list of paths.
    - paths ending with '/' => operations
    - others => file
    """
    paths = FS_MOCK_TEMPLATE
    root = Path(root_path)

    for route_string in paths:
        current_path: Path = root / route_string
        if route_string.endswith("/"):  # Creating empty folders
            current_path.mkdir(parents=True, exist_ok=True)
        else:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.write_text(f"{str(current_path)}")


@fixture
def valid_args_object(tmp_path: Path) -> Namespace:
    VALID_DEPTH: int = 1
    VALID_PATTERN: str = '.*\.txt'
    WORKSPACE_DIR_NAME = 'workspace'
    MAX_SIZE = 1024

    test_workspace_dir = tmp_path / WORKSPACE_DIR_NAME
    test_workspace_dir.mkdir()
    return Namespace(folder=test_workspace_dir, depth=VALID_DEPTH, pattern=VALID_PATTERN, max_size=MAX_SIZE)


def prone_fs_mock_by_depth(root_path: Path, depth: int) -> Set[Path]:
    mock_paths_list = set()
    for result_path in FS_MOCK_TEMPLATE:
        if result_path.count('/') < depth and not result_path.endswith('/'):
            full_path = root_path / result_path
            mock_paths_list.add(full_path)
    return mock_paths_list


