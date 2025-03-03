import encodings.utf_8
from io import BytesIO
from struct import unpack
from tools.map_extractor.definitions.objects.Vertex import Vertex


class Doodad:
    def __init__(self, mpq_entry):
        self.mpq_entry = mpq_entry
        self.vertices = []
        self.indices = []
        self.has_geometry = False
        self._read()

    def _read(self):
        data = self.mpq_entry.read_file_bytes()

        self.reader = BytesIO(data)
        with self.reader:
            magic = self.read_int()
            if magic != 1481393229:
                raise ValueError('INVALID_DOODAD_FILE.')
            version_magic = self.read_int()
            if version_magic != 1397900630:
                raise ValueError('UNEXPECTED_VERTEX_MAGIC_IN_ALPHA_MODEL.')
            version_size = self.read_int()
            if version_size != 4:
                raise ValueError('UNEXPECTED_VERSION_SIZE_IN_ALPHA_MODEL.')
            version = self.read_int()
            if version != 1300:
                raise ValueError('UNSUPPORTED_ALPHA_MODEL_VERSION.')

            # Offset to collision.
            self.reader.seek(0x5C)
            self.read_int()

            # Find DILC chunk.
            chunk_loc = self.get_chunk_location('DILC')
            if chunk_loc == -1:
                return

            self.reader.seek(chunk_loc + 8)

            vertex_magic = self.read_int()
            if vertex_magic != 1481921110:
                raise ValueError('UNEXPECTED_VERTEX_MAGIC_IN_ALPHA_MODEL.')

            vertex_count = self.read_int()
            vertices_pos = self.reader.tell()

            self.reader.seek(vertices_pos + vertex_count * 12)

            index_magic = self.read_int()
            if index_magic != 541676116:
                raise ValueError('UNEXPECTED_TRIANGLE_MAGIC_IN_ALPHA_MODEL.')

            index_count = self.read_int()
            indices_pos = self.reader.tell()

            if not vertex_count or not index_count:
                return

            self.reader.seek(vertices_pos)
            self.vertices = [Vertex(self.read_float(), self.read_float(), self.read_float())
                             for _ in range(vertex_count)]

            self.reader.seek(indices_pos)
            self.indices = [self.read_short() for _ in range(index_count)]

            self.has_geometry = len(self.vertices) > 0 and len(self.vertices) > 0


    def get_chunk_location(self, token_name):
        with self.reader.getbuffer() as buffer:
            buf_len = buffer.nbytes
            for i in range(4, buf_len):
                if i + 4 > buf_len:
                    return -1

                chunk = buffer[i:i + 4].tobytes()
                if (self.valida_chunk_char(chunk[0]) and self.valida_chunk_char(chunk[1])
                        and self.valida_chunk_char(chunk[2]) and self.valida_chunk_char(chunk[3])):
                    if encodings.utf_8.decode(chunk)[0][::-1] == token_name:
                        return i
        return -1

    def valida_chunk_char(self, byte):
        c = chr(byte)
        return ('A' <= c <= 'Z') or c == '2'

    def read_token(self):
        tmp_string = ''
        for i in range(4):
            tmp_string += self.read_char()
        return tmp_string

    def read_char(self):
        return chr(unpack('<B', self.reader.read(1))[0])

    def read_short(self):
        return unpack('<H', self.reader.read(2))[0]

    def read_int(self):
        return unpack('<I', self.reader.read(4))[0]

    def read_float(self):
        return unpack('<f', self.reader.read(4))[0]

    def read_string(self, terminator='\x00'):
        tmp_string = ''
        tmp_char = chr(unpack('<B', self.reader.read(1))[0])
        while tmp_char != terminator:
            tmp_string += tmp_char
            tmp_char = chr(unpack('<B', self.reader.read(1))[0])

        return tmp_string