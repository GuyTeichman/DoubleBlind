import csv
import fnmatch
import itertools
import warnings
from pathlib import Path
from typing import Union, Literal

from doubleblind import utils


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
            for file_path in self.root_dir.glob('*'):
                if file_path.is_file():
                    if any(fnmatch.fnmatch(file_path.name, f'*{fmt}') for fmt in self.included_file_types) and \
                            not any(fnmatch.fnmatch(file_path.name, f'*{fmt}') for fmt in self.excluded_file_types):
                        files.append(file_path)
        else:
            files = [item for item in self.root_dir.iterdir() if
                     item.is_file() and item.suffix.lower() in self.included_file_types and
                     item.suffix.lower() not in self.excluded_file_types]
        return files

    def write_outfile(self, decode_dict: dict):
        with open(self.root_dir.joinpath(self.FILENAME), 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(decode_dict.keys())
            writer.writerows(zip(decode_dict['encoded_name'], decode_dict['decoded_name']))

    def blind(self):
        assert self.root_dir.exists()
        decode_dict = {'encoded_name': [], 'decoded_name': []}

        try:
            for file in self.get_file_list():
                name = file.stem
                file_path = file
                new_name = utils.encode_filename(name)
                new_file_path = file.parent.joinpath(f"{new_name}{file.suffix}")
                file_path.replace(new_file_path)
                decode_dict['encoded_name'].append(new_name)
                decode_dict['decoded_name'].append(name)
        finally:
            self.write_outfile(decode_dict)

    def unblind(self):
        n_decoded = 0
        for file in self.get_file_list():
            name = file.stem
            file_path = file

            try:
                old_name = utils.decode_filename(name)
                old_file_path = file.parent.joinpath(f"{old_name}{file.suffix}")

                file_path.replace(old_file_path)
                n_decoded += 1
            except ValueError:
                warnings.warn(f'Could not decode file "{name}"')
        print("Filenames decoded successfully")


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

    def blind(self):
        assert self.root_dir.exists()
        decode_dict = {'encoded_name': [], 'decoded_name': []}

        try:
            for file in self.get_file_list():
                name = file.stem
                file_path = file
                conj_folder_path = file.parent.joinpath(f"_{file.stem}_")

                if not conj_folder_path.exists():
                    warnings.warn(f'Could not find the conjugate folder of file "{name}"')
                    continue

                new_name = utils.encode_filename(name)
                new_file_path = file.parent.joinpath(f"{new_name}{file.suffix}")

                new_conj_folder_path = conj_folder_path.parent.joinpath(f"_{new_name}_")

                file_path.replace(new_file_path)
                conj_folder_path.replace(new_conj_folder_path)

                decode_dict['encoded_name'].append(new_name)
                decode_dict['decoded_name'].append(name)
        finally:
            self.write_outfile(decode_dict)

    def unblind(self):
        n_decoded = 0
        for file in self.get_file_list():
            name = file.stem
            file_path = file
            conj_folder_path = file.parent.joinpath(f"_{file.stem}_")

            try:
                old_name = utils.decode_filename(name)
                old_file_path = file.parent.joinpath(f"{old_name}{file.suffix}")
                old_conj_folder_path = conj_folder_path.parent.joinpath(f"_{old_name}_")

                file_path.replace(old_file_path)
                conj_folder_path.replace(old_conj_folder_path)
                n_decoded += 1
            except ValueError:
                warnings.warn(f'Could not decode file "{name}"')
        print("Filenames decoded successfully")
