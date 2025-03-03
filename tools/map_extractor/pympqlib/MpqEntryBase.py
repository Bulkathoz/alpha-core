
class MpqEntryBase:
    def __init__(self, mpq_archive = None, file_path = None):
        self.filename = ''
        self.mpq_archive = mpq_archive
        self.file_path = file_path
        self.file_size = 0
        self.is_orphan = False

    def _sanitize(self):
        if self.filename.endswith('wmo.MPQ') or self.filename.endswith('wdl.MPQ') or self.filename.endswith('wdt.MPQ'):
            self.filename = self.filename[:-len('.MPQ')]

    def read_file_bytes(self):
        from tools.map_extractor.pympqlib.MpqReader import MpqReader
        from tools.map_extractor.pympqlib.MpqArchive import MpqArchive
        if self.is_orphan:
            with MpqArchive(filename=self.file_path, is_orphan=self.is_orphan) as archive:
                with MpqReader(archive, self) as mpq_reader:
                    return mpq_reader.data
        else:
            with MpqReader(self.mpq_archive, self) as mpq_reader:
                return mpq_reader.data
