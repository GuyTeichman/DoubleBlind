import csv
import fnmatch
import itertools
import warnings
from pathlib import Path
from typing import Union, Literal

from doubleblind import utils, editing


class GenericCoder:
    FILENAME = 'doubleblind_encoding.csv'

    def __init__(self, root_dir: Path, recursive: bool = True,
                 included_file_types: Union[set[str], Literal['all']] = 'all',
                 excluded_file_types: set[str] = frozenset()):
        self.root_dir = root_dir
        self.recursive = recursive
        self.included_file_types = included_file_types
        self.excluded_file_types = excluded_file_types

    def get_file_list(self):
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

    def write_outfile(self, decode_dict: dict, output_dir: Union[Path, None] = None):
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
    def get_coded_name(file_path: Path, original_name: str, decode_dict: dict):
        new_name = utils.encode_filename(original_name)
        new_file_path = file_path.parent.joinpath(f"{new_name}{file_path.suffix}")

        while new_name in decode_dict or new_file_path.exists():  # ensure no two files have the same coded name
            new_name = utils.encode_filename(original_name)
            new_file_path = file_path.parent.joinpath(f"{new_name}{file_path.suffix}")

        return new_name

    def blind(self, output_dir: Union[Path, None] = None):
        assert self.root_dir.exists()
        decode_dict = {}

        try:
            for file in self.get_file_list():
                name = file.stem
                file_path = file
                new_name = self.get_coded_name(file, name, decode_dict)

                new_file_path = file.parent.joinpath(f"{new_name}{file.suffix}")
                file_path.replace(new_file_path)
                decode_dict[new_name] = (name, file.as_posix())
        finally:
            self.write_outfile(decode_dict, output_dir)

    @staticmethod
    def _unblind_additionals(additional_files: Path, decode_dict: dict):
        unblinded = []
        if additional_files is None:
            return unblinded

        for item in additional_files.iterdir():
            if not item.is_file():
                continue
            if item.suffix in {'.xls', '.xlsx'}:
                unblinded.append(editing.edit_excel(item, decode_dict))
            elif item.suffix in {'.csv', '.tsv', '.txt', '.json'}:
                unblinded.append(editing.edit_text(item, decode_dict))
        return unblinded

    def unblind(self, additional_files: Path):
        decode_dict = {}
        n_decoded = 0
        for file in self.get_file_list():
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
    FORMATS = set(itertools.chain(utils.get_extensions_for_type('image'), utils.get_extensions_for_type('video')))

    def __init__(self, root_dir: Path, recursive: bool = True):
        super().__init__(root_dir, recursive, self.FORMATS)


class VSICoder(GenericCoder):
    def __init__(self, root_dir: Path, recursive: bool = True):
        super().__init__(root_dir, recursive, {'.vsi'})

    def get_file_list(self):
        if self.recursive:
            files = [item for item in self.root_dir.glob('**/*.vsi')]
        else:
            files = [item for item in self.root_dir.iterdir() if item.is_file() and item.suffix.lower() == '.vsi']
        return files

    def blind(self, output_dir: Union[Path, Literal[None]] = None):
        assert self.root_dir.exists()
        decode_dict = {}

        try:
            for file in self.get_file_list():
                name = file.stem
                file_path = file
                conj_folder_path = file.parent.joinpath(f"_{file.stem}_")

                if not conj_folder_path.exists():
                    warnings.warn(f'Could not find the conjugate folder of file "{name}"')
                    continue

                new_name = self.get_coded_name(file, name, decode_dict)

                new_file_path = file.parent.joinpath(f"{new_name}{file.suffix}")
                new_conj_folder_path = conj_folder_path.parent.joinpath(f"_{new_name}_")

                file_path.replace(new_file_path)
                conj_folder_path.replace(new_conj_folder_path)

                decode_dict[new_name] = (name, file.as_posix())
        finally:
            self.write_outfile(decode_dict, output_dir)

    def unblind(self, additional_files: Path):
        decode_dict = {}
        n_decoded = 0
        for file in self.get_file_list():
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
