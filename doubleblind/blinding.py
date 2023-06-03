import csv
import fnmatch
import itertools
import warnings
import zipfile
from pathlib import Path
from typing import Union, Literal, Set

from doubleblind import utils, editing


class GenericCoder:
    """
        A class for encoding and decoding files in a directory using a generic coding scheme.

        The GenericCoder class provides functionality for encoding files in a directory
        using a generic coding scheme, as well as decoding the encoded files back to their
        original names. It supports various file types and allows customization of the
        encoding process.

        Args:
            root_dir (Path): The root directory containing the files to be encoded/decoded.
            recursive (bool, optional): Flag indicating whether to perform the operation recursively
                on all subdirectories. Defaults to True.
            included_file_types (Union[Set[str], Literal['all']], optional): Set of file extensions
                to be included for encoding/decoding. Pass 'all' to include all file types.
                Defaults to 'all'.
            excluded_file_types (Set[str], optional): Set of file extensions to be excluded from
                encoding/decoding. Defaults to an empty set.

        Attributes:
            root_dir (Path): The root directory containing the files to be encoded/decoded.
            recursive (bool): Flag indicating whether to perform the operation recursively on
                all subdirectories.
            included_file_types (Set[str] or 'all'): Set of file extensions to be included for
                encoding/decoding. 'all' represents all file types.
            excluded_file_types (Set[str]): Set of file extensions to be excluded from encoding/decoding.

        """
    FILENAME = 'doubleblind_encoding.csv'

    def __init__(self, root_dir: Path, recursive: bool = True,
                 included_file_types: Union[Set[str], Literal['all']] = 'all',
                 excluded_file_types: Set[str] = frozenset()):
        self.root_dir = root_dir
        self.recursive = recursive
        self.included_file_types = included_file_types
        self.excluded_file_types = excluded_file_types

    def _get_file_list(self):
        if self.recursive:
            files = []
            for file_path in self.root_dir.glob('**/*'):
                if file_path.is_file():
                    if any(fnmatch.fnmatch(file_path.name, f'*{fmt}') for fmt in self.included_file_types) and \
                            not any(fnmatch.fnmatch(file_path.name, f'*{fmt}') for fmt in self.excluded_file_types):
                        files.append(file_path)
        else:
            files = [item for item in self.root_dir.iterdir() if
                     item.is_file() and item.suffix.lower() in self.included_file_types and
                     item.suffix.lower() not in self.excluded_file_types]
        return files

    def _write_outfile(self, decode_dict: dict, output_dir: Union[Path, None] = None):
        if output_dir is None:
            output_dir = self.root_dir
        else:
            assert output_dir.is_dir() and output_dir.exists(), f"Invalid output_dir!"
        with open(output_dir.joinpath(self.FILENAME), 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['encoded_name', 'decoded_name', 'file_path'])
            for coded, (decoded, path) in decode_dict.items():
                writer.writerow([coded, decoded, path])

    @staticmethod
    def _get_coded_name(file_path: Path, original_name: str, decode_dict: dict):
        new_name = utils.encode_filename(original_name)
        new_file_path = file_path.parent.joinpath(f"{new_name}{file_path.suffix}")

        while new_name in decode_dict or new_file_path.exists():  # ensure no two files have the same coded name
            new_name = utils.encode_filename(original_name)
            new_file_path = file_path.parent.joinpath(f"{new_name}{file_path.suffix}")

        return new_name

    def blind(self, output_dir: Union[Path, None] = None):
        """
        Blind (encode) the files in the directory.

        Args:
            output_dir (Path or None, optional): Directory to save the output file containing the \
            details of the blinded files. If None, the root directory is used. Defaults to None.

        """
        assert self.root_dir.exists()
        decode_dict = {}

        try:
            for file in self._get_file_list():
                name = file.stem
                file_path = file
                new_name = self._get_coded_name(file, name, decode_dict)

                new_file_path = file.parent.joinpath(f"{new_name}{file.suffix}")
                file_path.replace(new_file_path)
                decode_dict[new_name] = (name, file.as_posix())
        finally:
            self._write_outfile(decode_dict, output_dir)

    @staticmethod
    def _unblind_additionals(additional_files: Path, decode_dict: dict):
        unblinded = []
        if additional_files is None:
            return unblinded

        for item in additional_files.iterdir():
            if not item.is_file():
                continue
            if item.suffix in {'.xls', '.xlsx'}:
                try:
                    unblinded.append(editing.edit_excel(item, decode_dict))
                except zipfile.BadZipfile:
                    pass
            elif item.suffix in {'.csv', '.tsv', '.txt', '.json'}:
                unblinded.append(editing.edit_text(item, decode_dict))
        return [file for file in unblinded if file is not None]

    def unblind(self, additional_files: Union[Path, None]):
        """
        Unblind (decode) the files in the directory.

        Args:
            additional_files (Path): Path to the directory containing additional files to unblind. \
            DoubleBlind will search those files for the blinded names of the files and replace them \
            with the original filenames.

        Returns:
            List[object]: List of unblinded additional files.

        """
        decode_dict = {}
        n_decoded = 0
        for file in self._get_file_list():
            name = file.stem
            file_path = file

            try:
                old_name = utils.decode_filename(name)
                decode_dict[name] = old_name
                old_file_path = file.parent.joinpath(f"{old_name}{file.suffix}")

                file_path.replace(old_file_path)
                n_decoded += 1
            except ValueError:
                warnings.warn(f'Could not decode file "{name}"')

        others = self._unblind_additionals(additional_files, decode_dict)
        print("Filenames decoded successfully")
        return others


class ImageCoder(GenericCoder):
    """
    A class for encoding and decoding image and video files in a directory using a generic coding scheme.

    The ImageCoder class extends the GenericCoder class to provide specific functionality for encoding
    and decoding image and video files. It supports various image and video file formats and allows
    customization of the encoding process.

    Args:
        root_dir (Path): The root directory containing the image and video files to be encoded/decoded.
        recursive (bool, optional): Flag indicating whether to perform the operation recursively on
            all subdirectories. Defaults to True.
    """
    FORMATS = set(itertools.chain(utils.get_extensions_for_type('image'), utils.get_extensions_for_type('video')))

    def __init__(self, root_dir: Path, recursive: bool = True):
        super().__init__(root_dir, recursive, self.FORMATS)


class VSICoder(GenericCoder):
    """
    A class for encoding and decoding VSI (Virtual Slide Image) files in a directory using a generic coding scheme.

    The VSICoder class extends the GenericCoder class to provide specific functionality for encoding
    and decoding VSI files. It supports VSI file format and allows customization of the encoding process.

    Args:
        root_dir (Path): The root directory containing the VSI files to be encoded/decoded.
        recursive (bool, optional): Flag indicating whether to perform the operation recursively on
            all subdirectories. Defaults to True.

    """

    def __init__(self, root_dir: Path, recursive: bool = True):
        super().__init__(root_dir, recursive, {'.vsi'})

    def _get_file_list(self):
        if self.recursive:
            files = [item for item in self.root_dir.glob('**/*.vsi')]
        else:
            files = [item for item in self.root_dir.iterdir() if item.is_file() and item.suffix.lower() == '.vsi']

        filtered_files = []
        for file in files:
            if self._get_conjugate_path(file).exists():
                filtered_files.append(file)
            else:
                warnings.warn(f'Could not find the conjugate folder of file "{file.name}"')

        return filtered_files

    @staticmethod
    def _get_conjugate_path(vsi_file: Path):
        conj_folder_path = vsi_file.parent.joinpath(f"_{vsi_file.stem}_")
        return conj_folder_path

    def blind(self, output_dir: Union[Path, Literal[None]] = None):
        assert self.root_dir.exists()
        decode_dict = {}

        try:
            for file in self._get_file_list():
                name = file.stem
                file_path = file
                conj_folder_path = self._get_conjugate_path(file)

                if not conj_folder_path.exists():
                    warnings.warn(f'Could not find the conjugate folder of file "{name}"')
                    continue

                new_name = self._get_coded_name(file, name, decode_dict)

                new_file_path = file.parent.joinpath(f"{new_name}{file.suffix}")
                new_conj_folder_path = conj_folder_path.parent.joinpath(f"_{new_name}_")

                file_path.replace(new_file_path)
                conj_folder_path.replace(new_conj_folder_path)

                decode_dict[new_name] = (name, file.as_posix())
        finally:
            self._write_outfile(decode_dict, output_dir)

    def unblind(self, additional_files: Path):
        decode_dict = {}
        n_decoded = 0
        for file in self._get_file_list():
            name = file.stem
            file_path = file
            conj_folder_path = file.parent.joinpath(f"_{file.stem}_")

            try:
                old_name = utils.decode_filename(name)
                decode_dict[name] = old_name
                old_file_path = file.parent.joinpath(f"{old_name}{file.suffix}")
                old_conj_folder_path = conj_folder_path.parent.joinpath(f"_{old_name}_")

                file_path.replace(old_file_path)
                conj_folder_path.replace(old_conj_folder_path)
                n_decoded += 1
            except ValueError:
                warnings.warn(f'Could not decode file "{name}"')

        others = self._unblind_additionals(additional_files, decode_dict)
        print("Filenames decoded successfully")
        return others
