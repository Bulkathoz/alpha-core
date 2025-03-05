import os
from dataclasses import dataclass

@dataclass
class GameObjectDisplayInfo:
    id: int
    path: str
    filename: str

    @staticmethod
    def from_bytes(dbc_reader):
        _id: int = dbc_reader.read_int()
        path: str = dbc_reader.read_string()
        return GameObjectDisplayInfo(_id, path, os.path.basename(os.path.realpath(path.replace('\\', '/'))))
