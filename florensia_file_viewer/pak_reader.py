from struct import unpack
from typing import Dict, List


class PakReader:
    def __init__(self, pak_file_path: str):
        self.filepath = pak_file_path

        self._files = {}

        with open(self.filepath, "rb") as fp:
            self.fileCount = unpack("i", fp.read(4))[0]

            for i in range(self.fileCount):
                name = fp.read(260).decode("utf-8").replace("\0", "")
                offset = unpack("i", fp.read(4))[0]
                length = unpack("i", fp.read(4))[0]
                _ = fp.read(28)

                self._files[name] = {
                    "offset": offset,
                    "length": length
                }

    def read_content(self, fname: str) -> bytes:
        file_infos = self.files[fname]
        offset = file_infos["offset"]
        length = file_infos["length"]

        with open(self.filepath, "rb") as fp:
            fp.seek(offset, 0)
            return fp.read(length)

    @property
    def files(self) -> Dict:
        return self._files

    @property
    def filenames(self) -> List[str]:
        return self._files.keys()
