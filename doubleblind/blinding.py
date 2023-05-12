import fnmatch
import itertools
import json
import warnings
from pathlib import Path
from typing import Union, Literal

from doubleblind import utils


class GenericCoder:
    FILENAME = 'doubleblind_decode.json'

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

    def blind(self):
        assert self.root_dir.exists()
        name_gen = utils.random_word_gen()
        decode_dict = {}

        with open(self.root_dir.joinpath(self.FILENAME), 'w') as decode_dict_path:
            try:
                for file in self.get_file_list():
                    name = file.stem
                    file_path = file
                    new_name = next(name_gen)
                    new_file_path = file.parent.joinpath(f"{new_name}.vsi")
                    file_path.replace(new_file_path)
                    decode_dict[new_name] = name
            finally:
                decode_str = json.dumps(decode_dict)
                decode_dict_path.write(decode_str)

    def unblind(self, decode_dict: Union[dict, None] = None):
        if decode_dict is not None:
            assert isinstance(decode_dict, dict)
            warnings.warn(f"'decode_dict' was supplied, therefore the local '{self.FILENAME}' file will be ignored. ")
        else:
            decode_dict = json.load(self.root_dir.joinpath(self.FILENAME).open())

        n_decoded = 0
        for file in self.get_file_list():
            name = file.stem
            file_path = file

            if name in decode_dict:
                old_name = decode_dict[name]
                old_file_path = file.parent.joinpath(f"{old_name}.vsi")

                file_path.replace(old_file_path)
                n_decoded += 1
            else:
                warnings.warn(f'Could not decode file "{name}"')
        if n_decoded < len(decode_dict):
            warnings.warn(
                f"{len(decode_dict) - n_decoded} files from the decode dictionary could not be found and decoded. ")
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
            files = self.root_dir.glob('**/*.vsi')
        else:
            files = [item for item in self.root_dir.iterdir() if item.is_file() and item.suffix.lower() == '.vsi']
        return files

    def blind(self):
        assert self.root_dir.exists()
        name_gen = utils.random_word_gen()
        decode_dict = {}

        with open(self.root_dir.joinpath(self.FILENAME), 'w') as decode_dict_path:
            try:
                for file in self.get_file_list():
                    name = file.stem
                    file_path = file
                    conj_folder_path = file.parent.joinpath(f"_{file.stem}_")

                    if not conj_folder_path.exists():
                        warnings.warn(f'Could not find the conjugate folder of file "{name}"')
                        continue

                    new_name = next(name_gen)

                    new_file_path = file.parent.joinpath(f"{new_name}.vsi")
                    new_conj_folder_path = conj_folder_path.parent.joinpath(f"_{new_name}_")

                    file_path.replace(new_file_path)
                    conj_folder_path.replace(new_conj_folder_path)

                    decode_dict[new_name] = name
            finally:
                decode_str = json.dumps(decode_dict)
                decode_dict_path.write(decode_str)

    def unblind(self, decode_dict: Union[dict, None] = None):
        if decode_dict is not None:
            assert isinstance(decode_dict, dict)
            warnings.warn("'decode_dict' was supplied, therefore the local 'decode_dict.txt' file will be ignored. ")

        else:
            decode_dict = json.load(self.root_dir.joinpath(self.FILENAME).open())

        n_decoded = 0
        for file in self.get_file_list():
            name = file.stem
            file_path = file
            conj_folder_path = file.parent.joinpath(f"_{file.stem}_")

            if name in decode_dict:
                old_name = decode_dict[name]
                old_file_path = file.parent.joinpath(f"{old_name}.vsi")
                old_conj_folder_path = conj_folder_path.parent.joinpath(f"_{old_name}_")

                file_path.replace(old_file_path)
                conj_folder_path.replace(old_conj_folder_path)
                n_decoded += 1
            else:
                warnings.warn(f'Could not decode file "{name}"')
        if n_decoded < len(decode_dict):
            warnings.warn(
                f"{len(decode_dict) - n_decoded} files from the decode dictionary could not be found and decoded. ")
        print("Filenames decoded successfully")
