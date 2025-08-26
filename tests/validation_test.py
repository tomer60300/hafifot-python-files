from copy import deepcopy
from typing import Optional
import pytest

from schema.parser import Config, ArgsValidationError
from tests.infra import *



class TestsValid:
    @pytest.mark.parametrize(("archive_name", "archive_code"), ARCHIVE_CASES)
    @pytest.mark.parametrize("max_size", SIZES)
    @pytest.mark.parametrize("regex", REGEXES)
    @pytest.mark.parametrize("depth", DEPTHS)
    def test_validation_input_valid(self, tmp_path: Path, depth: int, regex: str, max_size,
                                    archive_name: Optional[Path], archive_code: str):

        config_obj = Config.build(folder=tmp_path, depth=depth, regex=regex, max_size=max_size,
                                  archive_name=archive_name, archive_code=archive_code)

        assert config_obj.folder == tmp_path
        assert config_obj.depth == depth
        assert config_obj.pattern.pattern == regex
        assert config_obj.max_size == max_size
        assert config_obj.archive_name == archive_name
        assert config_obj.archive_code == archive_code




class TestsInvalid:

    @pytest.mark.parametrize(
        "field,value",
        [
            ("folder", Path(r"C:\Users\madeup\not-exist")),
            ("folder", Path(r"")),
            ("depth", -5),
            ("depth", 0),
            ("pattern", "("),
            ("max_size", 0.5),
            ("max_size", -5),
        ],
        ids=["Directory-not-exist", "Empty-Directory-Name", "Negative-Depth: -5", "Zero-Depth: 0", "invalid_pattern",
             "Size-is-Float: 0.5", "Negative-size: -5"]
    )
    def test_validation_invalid_field(self, valid_args_object: Namespace, field, value):

        invalid_args_object = deepcopy(valid_args_object)
        setattr(invalid_args_object, field, value)
        with pytest.raises(ArgsValidationError):
            Config.build(folder=invalid_args_object.folder, depth=invalid_args_object.depth,
                         regex=invalid_args_object.pattern, max_size=invalid_args_object.max_size)