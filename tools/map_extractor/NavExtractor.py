import os

from tools.map_extractor.MapExtractor import REQUIRED_DBC
from tools.map_extractor.definitions.objects.Doodad import Doodad
from tools.map_extractor.definitions.objects.Wmo import Wmo
from tools.map_extractor.pydbclib.helpers.RequiredDbc import RequiredDbc
from utils.Logger import Logger
from utils.ConfigManager import config
from tools.map_extractor.pydbclib.DbcReader import DbcReader
from tools.map_extractor.helpers.DataHolders import DataHolders
from tools.map_extractor.pympqlib.MpqArchive import MpqArchive
from tools.map_extractor.pydbclib.structs.GameObjectDisplayInfo import GameObjectDisplayInfo

WOW_DATA_FOLDER = 'Data'
WOW_MAPS_FOLDER = 'World/Maps'
REQUIRED_DBC = {0 : RequiredDbc("dbc.MPQ"), 1 : RequiredDbc("model.MPQ")}


class NavExtractor:

    @staticmethod
    def run():
        # Validate WoW root.
        if not config.Extractor.Maps.wow_root_path:
            Logger.error('No wow root path provided. (World of Warcraft base directory)')
            exit()

        # Validate its existence.
        elif not os.path.exists(config.Extractor.Maps.wow_root_path):
            Logger.error(f'Data path "{config.Extractor.Maps.wow_root_path}" does not exist.')
            exit()

        # Validate /Data/.
        data_path = os.path.join(config.Extractor.Maps.wow_root_path, WOW_DATA_FOLDER)
        if not os.path.exists(data_path):
            Logger.error(f'Unable to locate {data_path}.')
            exit()

        # Validate dbc.MPQ.
        for required_dbc in REQUIRED_DBC.values():
            required_dbc.path = os.path.join(data_path, required_dbc.name)
            if not os.path.exists(required_dbc.path):
                Logger.error(f'Unable to locate {required_dbc.name}.')
                exit()

        # maps_path = os.path.join(data_path, WOW_MAPS_FOLDER)
        # if not os.path.exists(dbc_path):
        #     Logger.error(f'Unable to locate {WOW_MAPS_FOLDER}.')
        #     exit()
        #
        # # Validate /etc/maps.
        # map_files_path = PathManager.get_maps_path()
        # if not os.path.exists(map_files_path):
        #     Logger.error(f'Unable to locate {map_files_path}.')
        #     exit()
        #
        # # Flush existent files.
        # filelist = [f for f in os.listdir(map_files_path) if f.endswith(".map")]
        # if filelist:
        #     Logger.warning(f'Existent {len(filelist)} .map files will be deleted, continue? Y/N [Y]')
        #     if input().lower() in ['y', '']:
        #         [os.remove(os.path.join(map_files_path, file)) for file in filelist]
        #     else:
        #         exit()

        # Extract available maps and area tables from dbc.
        with MpqArchive(REQUIRED_DBC[0].path) as archive:
            go_dbc = archive.find_file('GameObjectDisplayInfo.dbc')
            if not go_dbc:
                Logger.error(f'Unable to locate GameObjectDisplayInfo.dbc')
            if not go_dbc:
                exit()

            with DbcReader(buffer=archive.read_file_bytes(go_dbc)) as dbc_reader:
                for dbc_go_data in dbc_reader.read_records_by_type(GameObjectDisplayInfo):
                    DataHolders.add_go_info(dbc_go_data)

        # Validate we have maps.
        if not DataHolders.GAMEOBJECT_DISPLAY_INFO:
            Logger.error(f'Unable to read gameobject display info from {REQUIRED_DBC[0]}.')
            exit()

        with MpqArchive(REQUIRED_DBC[1].path, orphans=True) as archive:
            for go_info in DataHolders.get_go_infos():
                file = archive.find_file(go_info.filename)
                # Check if Map.dbc data points to a valid wdt file.
                if not file:
                    Logger.warning(f'[{go_info.path}] does not exist as defined in GameObjectDisplayInfo.dbc, skipping.')
                    continue

                if file.filename.endswith('x'):
                    pass
                    #doodad = Doodad(file)
                    #if doodad.has_geometry:
                    #    Logger.info(f'[{go_info.filename}] has geometry defined.')
                else:
                    Logger.info(f'[{go_info.filename}] processing...')
                    wmo = Wmo(file)

        input()