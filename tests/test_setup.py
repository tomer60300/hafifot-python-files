import re
from argparse import Namespace
from copy import deepcopy
from pathlib import Path

import pytest

from config import Config, ArgsValidationError
from directory.search import walk_with_depth

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


class TestConfig:

    def _build_pattern_obj(self, regex: str) -> re.Pattern:
        return re.compile(regex)

    @pytest.fixture
    def valid_args_object(self, tmp_path: Path) -> Namespace:
        VALID_DEPTH: int = 1
        VALID_PATTERN: str = '.\.txt'
        WORKSPACE_DIR_NAME = 'workspace'
        SIZE = 1024

        test_workspace_dir = tmp_path / WORKSPACE_DIR_NAME
        test_workspace_dir.mkdir()
        return Namespace(folder=test_workspace_dir, depth=VALID_DEPTH, pattern=VALID_PATTERN, size=SIZE)

    @pytest.mark.parametrize("depth", [1, 2], ids=["immediate files -- 1", "subfolder depth -- 2"])
    @pytest.mark.parametrize("regex", [".\.txt", r"^(a+)+", r"^C:\\Users\\[A-Za-z0-9_]+\\Documents\\.*"],
                             ids=["textfile-regex-", "a-regex", "Documents-regex-"])
    @pytest.mark.parametrize("size", [0, 1024, 10485760, None], ids=["All Size", "1KB", "10MB", "No Size Given"])
    def test_validation_input_valid(self, tmp_path: Path, depth: int, regex: str, size: int):
        if size:
            config_obj = Config.build(folder=tmp_path, depth=depth, regex=regex, size=size)
            assert config_obj.size == size
        else:
            config_obj = Config.build(folder=tmp_path, depth=depth, regex=regex)

        assert config_obj.folder == tmp_path
        assert config_obj.depth == depth
        assert config_obj.pattern.pattern == regex

    @pytest.mark.parametrize(
        "field,value",
        [
            ("folder", Path(r"C:\Users\madeup\not-exist")),
            ("folder", Path(r"")),
            ("depth", -5),
            ("depth", 0),
            ("pattern", "("),
            ("size", 0.5),
            ("size", -5),
        ],
        ids=["dir_not_exist", "empty dir path", "Negative Depth -- -5", "Zero Depth -- 0", "invalid_pattern",
             "Zero size -- 0", "Negative size -- -5"]
    )
    def test_validation_invalid_field(self, valid_args_object: Namespace, field, value):

        invalid_args_object = deepcopy(valid_args_object)
        setattr(invalid_args_object, field, value)
        with pytest.raises(ArgsValidationError):
            Config.build(folder=invalid_args_object.folder, depth=invalid_args_object.depth,
                         regex=invalid_args_object.pattern, size=invalid_args_object.size)

    def test_validation_argument_valid(self):
        pass  # Todo

    def _create_fs_from_template(self, root_path: Path):
        """
        Create files and directories from a flat list of paths.
        - paths ending with '/' => directory
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

    @pytest.mark.parametrize("depth", [1, 2, 3],
                             ids=["immediate files - 1", "subdir included - 2", "sub-subdir included - 3"])
    def test_search_depth_filter(self, tmp_path: Path, depth: int):
        MATCH_ALL_PATTERN = re.compile(r".*")
        self._create_fs_from_template(root_path=tmp_path)  # Filesystem tree created
        result_paths_list = set(walk_with_depth(tmp_path, depth, MATCH_ALL_PATTERN))

        mock_paths_list = set()
        for result_path in FS_MOCK_TEMPLATE:
            if result_path.count('/') < depth and not result_path.endswith('/'):
                full_path = tmp_path / result_path
                mock_paths_list.add(full_path)
        assert result_paths_list == mock_paths_list

    def test_search_size_filter(self, tmp_path: Path):
        FIXED_DEPTH = 2
        FIXED_SIZE = 1023

        MATCH_ALL_PATTERN = re.compile(r".*")
        self._create_fs_from_template(root_path=tmp_path)


        size_flagged_file = Path(tmp_path / FS_MOCK_TEMPLATE[0])
        size_flagged_file.write_bytes(b"\0" * FIXED_SIZE)

        mock_paths_list = set()
        for result_path in FS_MOCK_TEMPLATE:
            if result_path.count('/') < FIXED_DEPTH and not result_path.endswith('/'):
                full_path = tmp_path / result_path
                mock_paths_list.add(full_path)

        filter_under_size = set(walk_with_depth(tmp_path, FIXED_DEPTH, MATCH_ALL_PATTERN,max_size=FIXED_SIZE-1))
        filter_equal_size = set(walk_with_depth(tmp_path, FIXED_DEPTH, MATCH_ALL_PATTERN,max_size=FIXED_SIZE))
        filter_above_size = set(walk_with_depth(tmp_path, FIXED_DEPTH, MATCH_ALL_PATTERN,max_size=FIXED_SIZE+1))

        assert filter_equal_size == mock_paths_list
        assert filter_above_size == mock_paths_list
        assert size_flagged_file in (filter_under_size ^ filter_above_size)



