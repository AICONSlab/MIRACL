import pytest
from argparse import Namespace
from types import SimpleNamespace
from pathlib import Path
from miracl.flow.miracl_workflow_ace_interface import RegistrationChecker
from miracl.flow.miracl_workflow_ace_parser import ACEWorkflowParser


def test_default_orientation_used() -> None:
    """
    Test that default orientation is used when no override flags are set.
    """
    args = SimpleNamespace(
        single="/tiff/stack/root/folder",
        rca_sep_orient_code=False,
        rca_autodetect_sep_orient_code=False,
        rca_orient_code="ALS",
    )
    result = RegistrationChecker.resolve_orientation(args)
    assert result == "ALS"


def test_sep_orient_code_from_file(tmp_path: Path) -> None:
    """
    Test that orientation.txt overrides the CLI orientation when --rca_sep_orient_code is set.
    """
    subject_dir = tmp_path
    (subject_dir / "orientation.txt").write_text("RAS")

    args = SimpleNamespace(
        single=str(subject_dir),
        rca_sep_orient_code=True,
        rca_autodetect_sep_orient_code=False,
        rca_orient_code="ALS",
    )

    result = RegistrationChecker.resolve_orientation(args)
    assert result == "RAS"


def test_sep_orient_file_missing_raises(tmp_path: Path) -> None:
    """
    Test that FileNotFoundError is raised if --rca_sep_orient_code is set but file is missing.
    """
    args = SimpleNamespace(
        single=str(tmp_path),
        rca_sep_orient_code=True,
        rca_autodetect_sep_orient_code=False,
        rca_orient_code="ALS",
    )

    with pytest.raises(FileNotFoundError):
        RegistrationChecker.resolve_orientation(args)


def test_sep_orient_file_invalid_raises(tmp_path: Path) -> None:
    """
    Test that ValueError is raised if orientation.txt contains an invalid orientation code.
    """
    (tmp_path / "orientation.txt").write_text("bad")

    args = SimpleNamespace(
        single=str(tmp_path),
        rca_sep_orient_code=True,
        rca_autodetect_sep_orient_code=False,
        rca_orient_code="ALS",
    )

    with pytest.raises(ValueError):
        RegistrationChecker.resolve_orientation(args)


def test_autodetect_orientation_used_when_file_exists(tmp_path: Path) -> None:
    """
    Test that autodetect uses orientation.txt when file is present and valid.
    """
    (tmp_path / "orientation.txt").write_text("LPI")

    args = SimpleNamespace(
        single=str(tmp_path),
        rca_sep_orient_code=False,
        rca_autodetect_sep_orient_code=True,
        rca_orient_code="ALS",
    )

    result = RegistrationChecker.resolve_orientation(args)
    assert result == "LPI"


def test_autodetect_orientation_falls_back_to_default(tmp_path: Path) -> None:
    """
    Test that autodetect falls back to rca_orient_code when file is missing.
    """
    args = SimpleNamespace(
        single=str(tmp_path),
        rca_sep_orient_code=False,
        rca_autodetect_sep_orient_code=True,
        rca_orient_code="ALS",
    )

    result = RegistrationChecker.resolve_orientation(args)
    assert result == "ALS"


def test_mutually_exclusive_orientation_flags_raises_error():
    """
    Test that rca_sep_orient_code and rca_autodetect_sep_orient_code can't be called together.
    """
    parser = ACEWorkflowParser()

    args = Namespace(
        single="/tiff/stack/root/folder",
        control=None,
        treated=None,
        rca_sep_orient_code=True,
        rca_autodetect_sep_orient_code=True,
        sa_output_folder="out",
        sa_model_type="unet",
        sa_resolution="3,3,3",
    )

    with pytest.raises(SystemExit):
        parser.validate_args(args)
