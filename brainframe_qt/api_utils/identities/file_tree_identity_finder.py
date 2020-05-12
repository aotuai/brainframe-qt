from pathlib import Path
import re
from typing import List
import ujson
import logging

from brainframe.client.api_utils.identities.identity_finder import (
    IdentityPrototype,
    IdentityFinder
)


class FileTreeIdentityFinder(IdentityFinder):
    """An IdentityFinder that can find identity prototypes from a predefined
    directory structure. This structure is documented in the BrainFrame manual,
    and is a bit too complicated to duplicate here.
    """

    def __init__(self, path: Path):
        self._path = path

        self.num_encodings = verify_directory_structure(path)

    def find(self) -> List[IdentityPrototype]:
        prototypes: List[IdentityPrototype] = []

        # Identities directories are named using the following format:
        #     identity_id (nickname)
        for identity_dir in self._path.iterdir():
            prototype = IdentityPrototype()

            # TODO: Better regex to avoid if-else
            if '(' not in identity_dir.name:
                # No nickname was specified
                prototype.unique_name = identity_dir.name
                prototype.nickname = None
            else:
                # A nickname was specified

                # This matches to names like "john_doe (Johnny Boy)"
                match = re.search(r"(.+?)\s*\((.*)\)", identity_dir.name)

                if not match:
                    logging.warning(f"FileTreeIdentityFinder: Unknown "
                                    f"directory name format {identity_dir}")
                    continue

                prototype.unique_name = match[1]
                prototype.nickname = match[2]

            # Iterate over encoding class types
            for class_dir in identity_dir.iterdir():
                for file_name in class_dir.iterdir():
                    data = file_name.read_bytes()

                    if file_name.suffix == ".json":
                        # The file is a vector
                        data_json = ujson.loads(data)
                        prototype.vectors_by_class_name[class_dir.name].append(
                            (file_name, data_json))
                    else:
                        # The file is probably an image
                        prototype.images_by_class_name[class_dir.name].append(
                            (file_name, data))

            prototypes.append(prototype)

        return prototypes


def verify_directory_structure(path: Path) -> int:
    """Verify that the directory is structured properly

    :return int: Number of future encodings in directory, for progress
        indication
    """
    num_encodings = 0

    if not path.is_dir():
        raise ValueError(f"Path {path} is not a directory.")

    if not path.iterdir():
        raise ValueError(f"Path {path} has no children")

    for identity_dir in path.iterdir():

        if not identity_dir.is_dir():
            raise ValueError(f"Identity {identity_dir} is not a directory.")

        for encoding_dir in identity_dir.iterdir():

            if not encoding_dir.is_dir():
                raise ValueError(f"Class {encoding_dir} is not a "
                                 f"directory.")

            for file_path in encoding_dir.iterdir():
                if not file_path.is_file():
                    raise ValueError(f"{file_path} is not a file.")

                num_encodings += 1

    return num_encodings
