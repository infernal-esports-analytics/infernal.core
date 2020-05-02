import context

import os
import sys
import json
import logging
from struct import unpack
from io import BufferedReader, SEEK_CUR, SEEK_END, SEEK_SET

import numpy
from PIL import Image

""" Logging Setup """
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Vector:
    
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'
    
    def __repr__(self):
        return f'Vector(x={self.x}, y={self.y}, z={self.z})'

    def __add__(self, other):
        return Vector(
            x=(self.x + other.x),
            y=(self.y + other.y),
            z=(self.z + other.z)
        )
    def __sub__(self, other):
        return Vector(
            x=(self.x - other.x),
            y=(self.y - other.y),
            z=(self.z - other.z)
        )

    
class Color:
    
    @property
    def channels(self):
        return {
            'red': self._red,
            'green': self._green,
            'blue': self._blue
        }
    
    @property
    def red(self):
        return self._red
    @property
    def r(self):
        return self._red
    
    @property
    def green(self):
        return self._green
    @property
    def g(self):
        return self._green
    
    @property
    def blue(self):
        return self._blue
    @property
    def b(self):
        return self._blue
    
    def __init__(self, red=0, green=0, blue=0):
        if any([
            not (0 <= red <= 255),
            not (0 <= green <= 255),
            not (0 <= blue <= 255)
        ]):
            raise ValueError('All values must be in range [0, 255]')
        
        
        self._red = red
        self._green = green
        self._blue = blue

    def __str__(self):
        return f'Color(red={self.r:03d}, blue={self.b:03d}, green={self.g:03d})'


class NGRIDFile:
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
        
        logger.debug(f'Reading file at {self._file_path}')
        logger.debug(f' => File Name:           {self._file_name}')
        logger.debug(f' => File Extension:      {self._file_ext}')
        
        self._file = open(self._file_path, 'rb')
        self._buffer = BufferedReader(self._file, self.BUFFER_SIZE)

    def __del__(self):
        self._file.close()



    """ Utility Methods """
    def seek(self, offset=-1, origin=SEEK_SET):
        if offset != -1 or origin != SEEK_SET:
            self._buffer.seek(offset, origin)

    def reset(self):
        self._buffer.seek(0)


    """ Read Methods """
    def read(self, len=None, offset=-1):
        try:
            self.seek(offset)

            if len is None:
                return self._buffer.read1()
            return self._buffer.read(len)
        except Exception as e:
            logger.exception(f'Could not read at {self.pos} due to {e}')
            return None

    def read_byte(self, offset=-1):
        try:
            return ord(self.read(1, offset))
        except Exception as e:
            logger.exception(f'Could not read byte at {self.pos} due to {e}')
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

    def read_int(self, offset=-1):
        try:
            data = self.read(4, offset)
            if sys.byteorder == 'big':
                return unpack('>I', data)[0]
            elif sys.byteorder == 'little':
                return unpack('<I', data)[0]

            logger.warning('Could not determin endianess of system.')
            return 0.0
        except Exception as e:
            logger.exception(f'Could not read int at {self.pos} due to {e}')
            return 0.0

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
            
    def read_short(self, offset=-1):
        try:
            data = self.read(2, offset)
            return unpack('h'*(len(data)//2), data)[0]

        except Exception as e:
            logger.exception(f'Could not read short at {self.pos} due to {e}')
            return 0

    def read_vector(self, offset=-1):
        return Vector(
            x=self.read_float(offset),
            y=self.read_float(),
            z=self.read_float()
        )


    def read_bool(self):
        pass

    def read_line(self):
        pass

    

    def read_color(self):
        pass


    """ Write Methods """


def get_cell(file):
    center_height = file.read_float()
    session_id = file.read_int()
    arrival_cost = file.read_float()
    cell_open = file.read_int()
    heuristic = file.read_float()

    cell_x = file.read_short()
    cell_z = file.read_short()

    actor_list = file.read_int()
    unknown_1 = file.read_int()
    goood_cell_session_id = file.read_int()
    weight_hint = file.read_float()
    unknown_2 = file.read_short()
    arrival_dir = file.read_short()
    hint_node_1 = file.read_short()
    hint_node_2 = file.read_short()

    full = {
        'x': cell_x,
        'z': cell_z,
        'height': center_height,
        'weight': weight_hint,
        'open': cell_open,
        'heuristic': heuristic,

        'arrival_cost': arrival_cost,
        'arrival_dir': arrival_dir,
        'actors': actor_list,

        'hints': [hint_node_1, hint_node_2],
        'sessions': [session_id, goood_cell_session_id],
        'unknowns': [unknown_1, unknown_2]
    }
    simple = {
        'x': cell_x,
        'z': cell_z,
        'height': center_height,
        'weight': weight_hint,
        'open': cell_open,
    }

    return simple, full


if __name__ == '__main__':
    file = NGRIDFile('srx.aimesh_ngrid')
    version = '.'.join([str(file.read_byte()), str(file.read_short())])
    logger.info(f'NGRID Version: {version}')

    _min, _max = file.read_vector(), file.read_vector()
    logger.info(f'Map Bounds: ({_min}, {_max})')
    logger.info(f'Map Size: {_max - _min}')

    _size = file.read_float()
    _countx, _countz = file.read_int(), file.read_int()
    logger.info(f'Cell Counts: ({_countx}, {_countz}) w/ Size: {_size}')

    cells = []
    _count = _countx * _countz
    for i in range(_count):
        cell, _ = get_cell(file)
        cell['index'] = i
        cells.append(cell)

    for i in range(_count):
        cells[i]['mask_vision'] = file.read_short()
    for i in range(_count):
        cells[i].update({
            'mask_river': file.read_byte(),
            'mask_jungle': file.read_byte(),
            'mask_neighborhood': file.read_byte(),
            'mask_srx': file.read_byte()
        })

    with open('cells.json', 'w') as f:
        json.dump(cells, f, indent=2)

    # trash section
    for i in range(8): 
        for j in range(132):
            file.read_byte()
    #

    """ Height Samples """

    _hcountx, _hcountz = file.read_int(), file.read_int()
    _hoffsetx, _hoffsetz = file.read_float(), file.read_float()
    logger.debug(f'Height Map Bounds: ({_hcountx}, {_hcountz})')
    logger.debug(f'Height Map Offests: ({_hoffsetx}, {_hoffsetz})')
