import os
from tools.map_extractor.pympqlib.MpqEntryBase import MpqEntryBase


class MpqOrphanEntry(MpqEntryBase):
    def __init__(self, mpq_archive, file_path):
        super().__init__(mpq_archive=mpq_archive, file_path=file_path)
        self.filename = os.path.basename(file_path)
        self.file_path = file_path
        self.file_size = os.path.getsize(self.file_path)
        self.is_orphan = True
        self._sanitize()
