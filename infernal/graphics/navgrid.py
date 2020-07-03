import os
import sys
import json
import logging
from enum import Enum, Flag, IntFlag, auto
from struct import unpack
from io import BufferedReader, SEEK_CUR, SEEK_END, SEEK_SET

import numpy as np


""" Logging Setup """
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

""" Enums & Flags """
class RiotNavGridType(Enum):
    AIMESH =                    'aimesh_ngrid'
    OVERLAY =                   'ngrid_overlay'

class RiotFlagsVisionPathing(Flag):
    WALKABLE =                  0

    BRUSH =                     auto() # 1
    WALL =                      auto() # 2
    WALL_STRUCTURE =            auto() # 4
    UNOBSERVED_A =              auto() # 8
    UNOBSERVED_B =              auto() # 16
    UNOBSERVED_C =              auto() # 32
    WALL_TRANSPARENT =          auto() # 64
    UNKNOWN_A =                 auto() # 128
    ALWAYS_VISIBLE =            auto() # 256
    UNKNOWN_B =                 auto() # 512
    BLUE_ZONE =                 auto() # 1024
    RED_ZONE =                  auto() # 2048
    NEUTRAL_ZONE =              auto() # 4096

    KNOWN = (
        WALKABLE | BRUSH | WALL | WALL_STRUCTURE | WALL_TRANSPARENT |
        ALWAYS_VISIBLE | BLUE_ZONE | RED_ZONE | NEUTRAL_ZONE
    )

class RiotFlagsRiverRegion(Flag):
    NON_JUNGLE =                0

    JUNGLE_QUADRANT =           auto() # 1
    BARON_PIT =                 auto() # 2
    UNOBSERVED_A =              auto() # 4
    UNOBSERVED_B =              auto() # 8
    RIVER =                     auto() # 16
    UNKNOWN_A =                 auto() # 32
    RIVER_ENTRANCE =            auto() # 64

    KNOWN = (
        NON_JUNGLE | JUNGLE_QUADRANT | BARON_PIT | RIVER | RIVER_ENTRANCE
    )

class RiotFlagsJungleQuadrant(IntFlag):
    NONE =                      0

    NORTH =                     1
    EAST =                      2
    WEST =                      3
    SOUTH =                     4

class RiotFlagsMainRegion(IntFlag):
    SPAWN =                     0
    BASE =                      1
    LANE_TOP =                  2
    LANE_MID =                  3
    LANE_BOT =                  4
    JUNGLE_TOP =                5
    JUNGLE_BOT =                6
    RIVER_TOP =                 7
    RIVER_BOT =                 8
    BASE_PERIM_TOP =            9
    BASE_PERIM_BOT =            10
    ALCOVE_TOP =                11
    ALCOVE_BOT =                12 

class RiotFlagsNearestLane(IntFlag):
    BLUE_TOP =                  0
    BLUE_MID =                  1
    BLUE_BOT =                  2
    RED_TOP =                   3
    RED_MID =                   4
    RED_BOT =                   5
    BLUE_NEUTRAL_TOP =          6
    BLUE_NEUTRAL_MID =          7
    BLUE_NEUTRAL_BOT =          8
    RED_NEUTRAL_TOP =           9
    RED_NEUTRAL_MID =           10
    RED_NEUTRAL_BOT =           11

class RiotFlagsPOI(IntFlag):
    NONE =                      0

    TURRET =                    1
    CLOUD_TUNNEL =              2

    # All others removed with S10? 

class RiotFlagsRings(IntFlag):
    BLUE_SPAWN_TO_NEXUS =       0
    BLUE_NEXUS_TO_INHIB =       1
    BLUE_INHIB_TO_INNER =       2
    BLUE_INHIB_TO_OUTER =       3
    BLUE_OUTER_TO_NEUTRAL =     4
    RED_SPAWN_TO_NEXUS =        5
    RED_NEXUS_TO_INHIB =        6
    RED_INHIB_TO_INNER =        7
    RED_INHIB_TO_OUTER =        8
    RED_OUTER_TO_NEUTRAL =      9

class RiotFlagsUnknownSRX(IntFlag):
    pass


""" Navgrid Bases """
class RiotNavGridFile:
    VALID_EXTS = ['aimesh_ngrid']
    BUFFER_SIZE = 8
    NULL = '\x00'


    @property
    def path(self):
        return self._file_path
    @property
    def name(self):
        return self._file_name
    @property
    def pos(self):
        return self._buffer.tell()
    @property
    def size(self):
        return self._size
    @property
    def kind(self):
        return self._kind


    def __init__(self, path, major=None, minor=None):
        self._file_path = os.path.abspath(path)
        if not os.path.exists(self._file_path):
            raise ValueError(f'No file found at {self._file_path}')

        self._file_name = (
            '.'.join(self._file_path.split('/')[-1].split('.')[:-1])
        )
        self._file_ext = self._file_path.split('.')[-1]
        if not self._file_ext in self.VALID_EXTS:
            raise TypeError(f'Invalid file type {self._file_ext}. Valid extensions are {self.VALID_EXTS}')

        self._kind = RiotNavGridType(self._file_ext)
        
        logger.debug(f'Reading file at {self._file_path}')
        logger.debug(f' => File Name:           {self._file_name}')
        logger.debug(f' => File Extension:      {self._file_ext}')
        
        self._file = open(self._file_path, 'rb')
        self._buffer = BufferedReader(self._file, self.BUFFER_SIZE)
        self._size = os.stat(self._file_path).st_size 

    def __del__(self):
        if hasattr(self, '_file'):
            self._file.close()


    """ Utility Methods """
    def seek(self, offset=-1, origin=SEEK_SET):
        if offset != -1 or origin != SEEK_SET:
            self._buffer.seek(offset, origin)

    def reset(self):
        self._buffer.seek(0)

    
    """ Read Methods """
    def read(self, size=None, offset=-1):
        try:
            self.seek(offset)
            if size is None:
                return self._buffer.read1()
            return self._buffer.read(size)
        except Exception as e:
            logger.exception(f'Could not read at {self.pos} due to {e}')
            return None

    def read_byte(self, offset=-1):
        try:
            return ord(self.read(1, offset))
        except Exception as e:
            logger.exception(f'Could not read byte at {self.pos} due to {e}')
            return 0

    def read_short(self, offset=-1):
        try:
            data = self.read(2, offset)
            return unpack('h'*(len(data)//2), data)[0]

        except Exception as e:
            logger.exception(f'Could not read short at {self.pos} due to {e}')
            return 0
    
    def read_float(self, offset=-1):
        try:
            data = self.read(4, offset)
            if sys.byteorder == 'big':
                return unpack('>f', data)[0]
            elif sys.byteorder == 'little':
                return unpack('<f', data)[0]

            logger.warning('Could not determin endianess of system.')
            return 0.0
        except Exception as e:
            logger.exception(f'Could not read float at {self.pos} due to {e}')
            return 0.0
    
    def read_int(self, offset=-1):
        try:
            data = self.read(4, offset)
            if sys.byteorder == 'big':
                return unpack('>I', data)[0]
            elif sys.byteorder == 'little':
                return unpack('<I', data)[0]

            logger.warning('Could not determin endianess of system.')
            return 0
        except Exception as e:
            logger.exception(f'Could not read int at {self.pos} due to {e}')
            return 0

    def read_char(self, offset=-1):
        try:
            return chr(self.read_byte(offset))
        except Exception as e:
            logger.exception(f'Could not read character at {self.pos} due to {e}')
            return self.NULL

    def read_string(self, length=-1, offset=-1):
        try:
            self.seek(offset)

            s = ''
            if length < 0:
                c = self.read_char()
                while c != self.NULL:
                    s += c
                    c = self.read_char()
            else:
                for _ in range(length):
                    s += c
            
            return s
        except Exception as e:
            logger.exception(f'Could not read string at {self.pos} due to {e}')
            return ''

    def read_bool(self, offset=-1):
        return bool(self.read_int())

    def read_vector(self):
        return (self.read_float(), self.read_float(), self.read_float())


class RiotNavGridReaderBase:

    @property
    def version(self):
        return '.'.join([*map(str,self._version)])


    def __init__(self, file):
        if not isinstance(file, RiotNavGridFile):
            raise ValueError(f'Expected RiotNagGridFile but got {type(file)}')
        
        self._file = file
        self._version = self._read_version()


    """ General Section Readers """
    # WARNING: These methods are not idempotent!
    def _read_version(self):
        return 0, 0


""" Navgrid Readers """
class RiotAimeshReader(RiotNavGridReaderBase):

    class RiotAimeshCell:
        def __init__(self, index, x, y, **params):
            self.index = index
            self.x, self.y = x, y
            self.params = params

            self.has_override = None

            # Flags
            self.flags_vision_pathing = None
            self.flags_river_region = None
            self.flags_jungle_quadrant = None
            self.flags_main_region = None
            self.flags_nearest_lane = None
            self.flags_poi = None
            self.flags_rings = None
            self.flags_unknown_srx = None

        def __str__(self):
            return f'[{self.index:05d}] <<{self.x:03d}, {self.y:03d}>>'


    def __init__(self, file):
        super().__init__(file=file)

        # Get map dimensions
        self._map_bounds = self._file.read_vector(), self._file.read_vector()
        self._map_size = tuple(map(lambda x,y:y-x, *self._map_bounds))

        # Get cell dimensions
        self._cell_size = self._file.read_float()
        self._cell_counts = self._file.read_int(), self._file.read_int()
        self._total_cell_count = self._cell_counts[0] * self._cell_counts[1]

        # Get cell data
        self._cells = []
        if self._version[0] == 7:
            self._cells = self._read_cells_curr()
        elif self._version[0] in [2,3,5]:
            self._cells = self._read_cells_prev()
        
        # Update heights, hints, flags
        self._height_samples, self._height_norms = self._read_heights()
        # self._hints = self._read_hints()
        # self._flags = self._read_flags()

        


    """ Section Readers """
    # WARNING: These methods are not idempotent!
    def _read_version(self):
        _major, _minor = self._file.read_byte(), 0
        if _major != 2:
            _minor = self._file.read_short()

        if _major not in ([7,5,3,2]):
            logger.warning(f'Unsupported version {_major}.{_minor}')
        
        return _major, _minor

    def _read_cells_curr(self):
        cells = []
        for i in range(self._total_cell_count):
            _center_height = self._file.read_float()
            _session_id = self._file.read_int()
            _arrival_cost = self._file.read_float()
            _is_open = self._file.read_int()
            _heuristic = self._file.read_float()

            x, y = self._file.read_short(), self._file.read_short()

            _actor_list = self._file.read_int()
            _unknown_0 = self._file.read_int()
            _good_cell_session_id = self._file.read_int()
            _hint_weight = self._file.read_float()
            _unknown_1 = self._file.read_short()
            _arrival_destination = self._file.read_short()
            _hint_node_0 = self._file.read_short()
            _hint_node_1 = self._file.read_short()

            cells.append(self.RiotAimeshCell(i, x, y))

        # Set vision pathing flags
        for cell in cells:
            cell.flags_vision_pathing = RiotFlagsVisionPathing(
                self._file.read_short()
            )

        # Set all other flags
        for cell in cells:
            cell.flags_river_region = RiotFlagsRiverRegion(
                self._file.read_byte()
            )
            
            _jung_main_region_flags = self._file.read_byte()
            cell.flags_jungle_quadrant = RiotFlagsJungleQuadrant(
                _jung_main_region_flags & 15
            )
            cell.flags_main_region = RiotFlagsMainRegion(
                (_jung_main_region_flags & ~15) >> 4
            )

            _lane_poi_region_falgs = self._file.read_byte()
            cell.flags_nearest_lane = RiotFlagsNearestLane(
                _lane_poi_region_falgs & 15
            )
            cell.flags_poi = RiotFlagsPOI(
                (_lane_poi_region_falgs & ~15) >> 4
            )

            _ring_srx_region_flags = self._file.read_byte()
            cell.flags_rings = RiotFlagsRings(
                _ring_srx_region_flags & 15
            )
            cell.flags_unknown_srx = RiotFlagsUnknownSRX(
                (_ring_srx_region_flags & ~15) >> 4
            )

        # Process unknown region
        for _ in range(8):
            for _ in range(132):
                self._file.read_byte()

        return cells

    def _read_cells_prev(self):
        cells = []
        for i in range(self._total_cell_count):
            x, y = None, None
            cell = self.RiotAimeshCell()

        return cells

    def _read_heights(self):
        _count_x, _count_z = self._file.read_int(), self._file.read_int()
        _offset_x, _offset_z = self._file.read_float(), self._file.read_float()


        heights = []
        _min, _max = 0, 0
        for i in range(_count_x * _count_z):
            _sample = self._file.read_float()

            if (i == 0) or (_sample < _min):
                _min = _sample
            if (i == 0) or (_sample > _max):
                _max = _sample

            heights.append(_sample)

        _norm = _max - _min
        norms = [(h-_min)/_norm for h in heights]
            
        return heights, norms



    def _read_hints(self):
        pass

    def _read_flags(self):
        pass


class RiotOverlayReader(RiotNavGridReaderBase):
    
    def __init__(self, file):
        super().__init__(file=file)


    """ Section Readers """
    # WARNING: These methods are not idempotent!
    def _read_version(self):
        _major, _minor = self._file.read_byte(), self._file.read_byte()

        if _major != 1 and _minor != 1:
            logger.warning(f'Unsupported version {_major}.{_minor}')

        return _major, _minor
