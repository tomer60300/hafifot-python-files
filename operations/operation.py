import os
import re
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Iterator, Union, Generator, Callable
from zipfile import ZipFile, ZIP_DEFLATED
from pyzipper import AESZipFile, WZ_AES
import logging
from schema.parser import Config

logger = logging.getLogger(__name__)

def _add_file_to_archive(archive_name: Path, file_path_obj: Path):
    with ZipFile(archive_name, "a", compression=ZIP_DEFLATED) as archive_file:
        _add_unique_file_to_zip(archive_file, file_path_obj)


def _add_file_to_locked_archive(archive_name: Path, file_path_obj: Path, archive_code: str) -> None:
    with AESZipFile(archive_name, mode="a", compression=ZIP_DEFLATED, encryption=WZ_AES) as archive_file:
        archive_file.setpassword(archive_code.encode("utf-8"))

        _add_unique_file_to_zip(archive_file, file_path_obj)





@dataclass(frozen=True)
class Mode:
    size_filter: bool
    archive_filter: bool
    archive_lock_filter: bool

    def run(self, **kwargs):
        state_to_mode_table = {
            (False, False): None,
            (True, False): _add_file_to_archive,
            (True, True): _add_file_to_locked_archive,
        }
        operation_func = state_to_mode_table[(self.archive_filter, self.archive_lock_filter)]
        if operation_func is not None:
            operation_func(**kwargs)



def execute(config: Config):
    mode = operation_mode_recognized(config)
    logger.debug(f"Mode: {mode}")

    for result in scan_filesystem_with_filter(**vars(config), mode=mode):
        print(f"{result} -- ", end="")


def operation_mode_recognized(config) -> Mode:
    should_compress = config.archive_name is not None
    should_lock = config.archive_code is not None
    use_size = config.max_size is not None
    return Mode(size_filter=use_size, archive_filter=should_compress, archive_lock_filter=should_lock)


def _add_unique_file_to_zip(archive_file: Union[ZipFile, AESZipFile], file_path_obj: Path):
    file_name = file_path_obj.name
    exist_names_in_archive = set(archive_file.namelist())
    if file_name in exist_names_in_archive:
        stem, suffix = file_path_obj.stem, file_path_obj.suffix
        index = 1
        while True:
            candidate = f"{stem}-{index}.{suffix}"
            if candidate not in exist_names_in_archive:
                file_name = candidate
                break
            index += 1

    archive_file.write(file_path_obj, arcname=file_name)


def scan_filesystem_with_filter(folder: Path, depth: int, pattern: re.Pattern, mode: Mode, max_size: int = 0,
                                archive_name: Path = None, archive_code: str = None) -> Iterator[Path]:
    """
    Iterate over files in the filesystem starting from `folder` and as deep as `depth`
    :param folder: the root folder to start scanning from
    :param depth: the maximum depth to scan ( 1-> immediate files, 2-> include subfolders, etc.)
    :param max_size: maximum file size in bytes ( equal included )
    :param archive_name -> archive matched file in archive_name
    :param archive_code -> locked archive_name with archive_code
    """
    root = folder.resolve()
    top_depth = len(root.parts)

    for dirpath, dirnames, filenames in os.walk(root):
        current_depth = len(Path(dirpath).parts) - top_depth

        for file in filenames:
            file_path_obj = Path(dirpath) / file

            if not pattern.match(file):
                continue
            if mode.size_filter and file_path_obj.stat().st_size > max_size:
                continue

            all_operation_params = {
                "archive_name": archive_name,
                "file_path_obj": file_path_obj,
                "archive_code": archive_code,
            }

            current_operation_params = {k: v for k, v in all_operation_params.items() if v is not None}
            mode.run(**current_operation_params)


            yield file_path_obj



        # prune dirs if max depth reached
        if current_depth >= depth - 1:
            logger.debug(f"Reached max depth: Depth: {current_depth},root-dir:{dirpath} pruning {dirnames}")
            dirnames.clear()  # don't go deeper
