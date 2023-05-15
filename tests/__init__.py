import filecmp
import os
import shutil
from pathlib import Path

import pandas as pd


def unlink_tree(dir):
    for item in Path(dir).iterdir():
        if 'gitignore' in item.name:
            continue
        if item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)


def are_dir_trees_equal(dir1, dir2, compare_contents: bool = True):
    """
    Compare two directories recursively. Files in each directory are \
    assumed to be equal if their names and contents are equal.\
    credit: bhttps://stackoverflow.com/a/6681395

    :param dir1: First directory path
    :param dir2: Second directory path

    :return: True if the dir trees are the same and there were no errors while accessing the directories or files, \
    False otherwise.
   """

    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or \
            len(dirs_cmp.funny_files) > 0:
        print(f"mismatch between {dir1} and {dir2} with left_only={dirs_cmp.left_only}, "
              f"right_only={dirs_cmp.right_only}, funny={dirs_cmp.funny_files}")
        return False
    (_, mismatch, errors) = filecmp.cmpfiles(
        dir1, dir2, dirs_cmp.common_files, shallow=False)
    if (len(mismatch) > 0 or len(errors) > 0) and compare_contents:
        print(f"mismatch between {dir1} and {dir2} in the files {mismatch} with errors {errors}")
        return False
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = Path(dir1).joinpath(common_dir).as_posix()
        new_dir2 = Path(dir2).joinpath(common_dir).as_posix()
        if not are_dir_trees_equal(new_dir1, new_dir2, compare_contents):
            return False
    return True


def compare_excel_files(file1_path, file2_path):
    # Read the Excel files into pandas DataFrames
    df1 = pd.read_excel(file1_path, sheet_name=None)
    df2 = pd.read_excel(file2_path, sheet_name=None)

    # Get the sheet names from both files
    sheet_names1 = set(df1.keys())
    sheet_names2 = set(df2.keys())

    # Check if the sheet names are the same
    if sheet_names1 != sheet_names2:
        return False

    # Compare the content of each sheet
    for sheet_name in sheet_names1:
        df1_sheet = df1[sheet_name]
        df2_sheet = df2[sheet_name]

        # Check if the sheet contents are the same
        if not df1_sheet.equals(df2_sheet):
            return False

    # All sheets are identical
    return True


if os.getcwd().endswith('tests'):
    try:
        os.chdir('../../DoubleBlind')
    except FileNotFoundError:
        pass
