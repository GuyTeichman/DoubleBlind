import pytest

from doubleblind.blinding import *
from tests import unlink_tree, are_dir_trees_equal, compare_excel_files


@pytest.fixture(params=[
    (True, {'.txt', }),
    (True, {'.txt', '.xls'}),
    (False, {'.jpg', '.csv'})
])
def generic_coder(request, tmp_path):
    recursive, included_file_formats = request.param
    root_dir = tmp_path / "test_dir"
    root_dir.mkdir()
    (root_dir / "subdir").mkdir()

    # Create some test files
    files = [
        root_dir / "file1.txt",
        root_dir / "file2.csv",
        root_dir / "file3.xls",
        root_dir / "file4.xlsx",
        root_dir / "file5.jpg",
        root_dir / "subdir" / "file6.txt",
    ]

    for file in files:
        file.touch()

    yield GenericCoder(root_dir, recursive, included_file_formats)

    # Cleanup the test files
    unlink_tree(root_dir)


def test_get_file_list(generic_coder):
    recursive = generic_coder.recursive
    file_types = generic_coder.included_file_types
    expected_files = {
        "file1.txt",
        "file2.csv",
        "file3.xls",
        "file4.xlsx",
        "file5.jpg",
        "file6.txt",
    }
    if not recursive:
        expected_files.remove('file6.txt')
    for file in expected_files.copy():
        match = False
        for suffix in file_types:
            if file.endswith(suffix):
                match = True
        if not match:
            expected_files.remove(file)

    files = generic_coder.get_file_list()
    assert len(files) == len(expected_files)
    assert set(file.name for file in files) == expected_files


def test_write_outfile(tmp_path):
    decode_dict = {
        "code1": ("name1", "path1"),
        "code2": ("name2", "path2"),
    }
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_file = output_dir / "doubleblind_encoding.csv"

    generic_coder = GenericCoder(Path("."))  # Using a dummy root_dir

    # Write the outfile
    generic_coder.write_outfile(decode_dict, output_dir)

    # Read the outfile and verify its contents
    with open(output_file, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)

    assert rows[0] == ["encoded_name", "decoded_name", "file_path"]
    assert rows[1] == ["code1", "name1", "path1"]
    assert rows[2] == ["code2", "name2", "path2"]

    # Cleanup the output directory
    output_file.unlink()
    output_dir.rmdir()


def test_get_coded_name(generic_coder, monkeypatch):
    file_path = Path("path/to/file.txt")
    original_name = "file"
    decode_dict = {
        "code1": ("name1", "path1"),
        "code2": ("name2", "path2"),
    }

    # Mock the utils.encode_filename function to always return "new_name"
    def mock_encode_filename(name):
        return "new_name"

    monkeypatch.setattr(utils, 'encode_filename', mock_encode_filename)
    new_name = generic_coder.get_coded_name(file_path, original_name, decode_dict)

    assert new_name == "new_name"
    assert not any(new_name in decoded for decoded, _ in decode_dict.values())


def test_blind(generic_coder, monkeypatch):
    recursive = generic_coder.recursive
    file_types = generic_coder.included_file_types

    # Prepare the encoded files
    encode_dict = {
        "file1": ('decoded1', "file1.txt"),
        "file2": ('decoded2', "file2.csv",),
        "file3": ('decoded3', "file3.xls",),
        "file4": ('decoded4', "file4.xlsx",),
        "file5": ('decoded5', "file5.jpg"),
        "file6": ('decoded6', "file6.txt"),
    }
    exp_files = []
    for code, (decoded, pth) in encode_dict.items():
        suffix = Path(pth).suffix
        if code == 'file6':
            if recursive and suffix in file_types:
                file_path = (generic_coder.root_dir / 'subdir' / decoded).with_suffix(suffix)
            else:
                file_path = generic_coder.root_dir / 'subdir' / pth
        elif suffix in file_types:
            file_path = (generic_coder.root_dir / decoded).with_suffix(suffix)
        else:
            file_path = generic_coder.root_dir / pth
        exp_files.append(file_path)

    # Mock the utils.decode_filename function to return the original name
    def mock_encode_filename(text):
        return encode_dict[text][0]

    monkeypatch.setattr(utils, 'encode_filename', mock_encode_filename)

    # Perform the unblind operation
    generic_coder.blind(None)

    # Verify that the files have been renamed back to the original names
    for file in exp_files:
        assert file.exists()
        if file.stem not in encode_dict:
            orig_path = file.parent.joinpath(f'file{file.stem[-1]}').with_suffix(file.suffix)
            assert not orig_path.exists()


def test_unblind(generic_coder, monkeypatch):
    recursive = generic_coder.recursive
    file_types = generic_coder.included_file_types

    # Prepare the encoded files
    encode_dict = {
        "file1": ('decoded1', "file1.txt"),
        "file2": ('decoded2', "file2.csv",),
        "file3": ('decoded3', "file3.xls",),
        "file4": ('decoded4', "file4.xlsx",),
        "file5": ('decoded5', "file5.jpg"),
        "file6": ('decoded6', "file6.txt"),
    }
    exp_files = []
    for code, (decoded, pth) in encode_dict.items():
        suffix = Path(pth).suffix
        if code == 'file6':
            if recursive and suffix in file_types:
                file_path = (generic_coder.root_dir / 'subdir' / decoded).with_suffix(suffix)
            else:
                file_path = generic_coder.root_dir / 'subdir' / pth
        elif suffix in file_types:
            file_path = (generic_coder.root_dir / decoded).with_suffix(suffix)
        else:
            file_path = generic_coder.root_dir / pth
        exp_files.append(file_path)

    # Mock the utils.decode_filename function to return the original name
    def mock_decode_filename(ciphertext):
        return encode_dict[ciphertext][0]

    monkeypatch.setattr(utils, 'decode_filename', mock_decode_filename)

    # Perform the unblind operation
    additional_files = None
    generic_coder.unblind(additional_files)

    # Verify that the files have been renamed back to the original names
    for file in exp_files:
        assert file.exists()
        if file.stem not in encode_dict:
            orig_path = file.parent.joinpath(f'file{file.stem[-1]}').with_suffix(file.suffix)
            assert not orig_path.exists()


def test_unblind_additional_files_edit(generic_coder, tmp_path, monkeypatch):
    decode_dict = {
        "code1": "name1",
        "code2": "name2",
    }
    additional_files = tmp_path / "additional"
    additional_files.mkdir()

    # Create some additional test files
    files = [
        additional_files / "file1.xls",
        additional_files / "file2.xlsx",
        additional_files / "file3.csv",
        additional_files / "file4.txt",
    ]

    for file in files:
        file.touch()

    # Mock the editing.edit_excel and editing.edit_text functions to return the unblinded files
    def mock_edit_excel(file, decode_dict):
        return f"Unblinded Excel file: {file.name}"

    def mock_edit_text(file, decode_dict):
        return f"Unblinded Text file: {file.name}"

    monkeypatch.setattr(editing, 'edit_excel', mock_edit_excel)
    monkeypatch.setattr(editing, 'edit_text', mock_edit_text)

    # Perform the unblind operation
    unblinded_files = generic_coder._unblind_additionals(additional_files, decode_dict)

    # Verify that the additional files have been processed correctly
    expected_unblinded_files = [
        "Unblinded Excel file: file1.xls",
        "Unblinded Excel file: file2.xlsx",
        "Unblinded Text file: file3.csv",
        "Unblinded Text file: file4.txt",
    ]
    assert unblinded_files == expected_unblinded_files

    # Cleanup the additional files
    for file in files:
        file.unlink()


def test_unblind_additional_files_content():
    decode_dict = {
        "code1": "name1",
        "code2": "name2",
    }
    additional_files = Path('tests/test_files/root_dir')

    # Perform the unblind operation
    unblinded_files = GenericCoder._unblind_additionals(additional_files, decode_dict)
    try:
        for file in unblinded_files:
            assert file.exists()

        assert are_dir_trees_equal('tests/test_files/root_dir', 'tests/test_files/unblind_additionals_truth',
                                   compare_contents=False)

        with open("tests/test_files/unblind_additionals_truth/dont_map_unblinded.txt") as f1, open(
                "tests/test_files/root_dir/dont_map_unblinded.txt") as f2:
            assert f1.read() == f2.read()

        assert compare_excel_files('tests/test_files/unblind_additionals_truth/test workbook_unblinded.xlsx',
                                   'tests/test_files/root_dir/test workbook_unblinded.xlsx')


    # Cleanup the additional files
    finally:
        for file in unblinded_files:
            file.unlink()
