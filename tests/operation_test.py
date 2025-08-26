from copy import deepcopy
import pytest

from schema.parser import Config, ArgsValidationError
from operations.operation import scan_filesystem_with_filter, Mode
from tests.infra import *

pytest_plugins = ["tests.infra"]

@pytest.mark.parametrize("depth", [1, 2, 3],
                         ids=["immediate files - 1", "subdir included - 2", "sub-subdir included - 3"])
def test_scan_op_no_filters(tmp_path: Path, depth: int):
    create_fs_from_template(root_path=tmp_path)  # Filesystem tree created

    result_paths_list = set(
        scan_filesystem_with_filter(folder=tmp_path, depth=depth, pattern=MATCH_ALL_PATTERN, mode=NO_FILTER_MODE))
    mock_paths_list = prone_fs_mock_by_depth(tmp_path, depth)
    assert result_paths_list == mock_paths_list


@pytest.mark.parametrize("delta,label", [(-1, "under"), (0, "equal"), (1, "above")])
def test_scan_op_size_filter(tmp_path: Path, delta: int, label: str):
    FIXED_DEPTH = 2
    FIXED_SIZE = 1023

    create_fs_from_template(root_path=tmp_path)

    size_flagged_file = Path(tmp_path / FS_MOCK_TEMPLATE[0])
    size_flagged_file.write_bytes(b"\0" * FIXED_SIZE)

    mock_paths_list = prone_fs_mock_by_depth(tmp_path, depth=FIXED_DEPTH)

    result_filter = {
        label: set(scan_filesystem_with_filter(
            tmp_path,
            depth=FIXED_DEPTH,
            pattern=MATCH_ALL_PATTERN,
            max_size=size,
            mode=SIZE_FILTER_MODE,
        ))
        for label, size in {
            "under": FIXED_SIZE - 1,
            "equal": FIXED_SIZE,
            "above": FIXED_SIZE + 1,
        }.items()
    }

    assert result_filter["equal"] == mock_paths_list
    assert result_filter["above"] == mock_paths_list
    assert size_flagged_file in (
            result_filter["under"] ^ mock_paths_list)  # The file generate with specific size should not be in under


@pytest.mark.parametrize("mode", [ARCHIVE_FILTER_MODE, LOCK_FILTER_MODE], ids=["archive-filter", "lock-filter"])
def test_scan_op_archive_filter(tmp_path: Path, mode: Mode):
    create_fs_from_template(root_path=tmp_path)  # Filesystem tree created

    passcode = "1234" if mode.archive_lock_filter else None
    result_paths_list = set(
        scan_filesystem_with_filter(folder=tmp_path, depth=SUB_SUB_DIR_DEPTH, pattern=MATCH_ALL_PATTERN,
                                    archive_name=Path("archive.zip"), archive_code=passcode, mode=mode))
    mock_paths_list = prone_fs_mock_by_depth(tmp_path, SUB_SUB_DIR_DEPTH)
    assert result_paths_list == mock_paths_list


@pytest.mark.parametrize(("field", "mode"), [("max_size", SIZE_FILTER_MODE), ("archive_name", ARCHIVE_FILTER_MODE),
                                                ("archive_code", LOCK_FILTER_MODE)],
                         ids=["max_size_filter_without_size", "archive-filter-without-zip-file",
                              "lock-filter-without-code"])
def test_scan_op_invalid_filters(tmp_path: Path, field: str,mode: Mode):
    create_fs_from_template(root_path=tmp_path)  # Filesystem tree created

    archive_name = Path("archive.zip") if not field == "archive_name" else None
    max_size = 1024 if not field == "max_size" else None

    with pytest.raises(TypeError):
        set(
            scan_filesystem_with_filter(folder=tmp_path, depth=SUB_SUB_DIR_DEPTH, pattern=MATCH_ALL_PATTERN,
                                        archive_name=archive_name, archive_code=None, max_size=max_size, mode=mode))
