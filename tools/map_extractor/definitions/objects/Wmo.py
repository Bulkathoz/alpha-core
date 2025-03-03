import encodings
from io import BytesIO
from struct import unpack


class Wmo:
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
            mver_loc = self.get_chunk_location('MVER')
            if mver_loc == -1:
                raise ValueError('MVER_NOT_FOUND.')

            self.reader.seek(mver_loc + 8)
            version = self.read_int()
            if version != 14:
                raise ValueError('UNSUPPORTED_ALPHA_WMO_VERSION.')

            momo_loc = self.get_chunk_location('MOMO')
            if momo_loc == -1:
                raise ValueError('MOMO_NOT_FOUND.')

            mohd_loc = self.get_chunk_location('MOHD')
            if mohd_loc == -1:
                raise ValueError('MOHD_NOT_FOUND.')

    def get_chunk_location(self, token_name, start_post=0):
        with self.reader.getbuffer() as buffer:
            buf_len = buffer.nbytes
            for i in range(start_post, buf_len):
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