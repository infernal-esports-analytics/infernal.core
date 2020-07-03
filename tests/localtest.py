import context

import os
import re
import sys
import json
import logging
import functools

from io import SEEK_END

from infernal.common import utils as u
from infernal.core import static as s
from infernal.core.service import create_service
from infernal.graphics import navgrid as ng



ng_file = ng.RiotNavGridFile('srx.aimesh_ngrid')
aimesh = ng.RiotAimeshReader(ng_file)

# for cell in aimesh._cells:
#     print(cell)