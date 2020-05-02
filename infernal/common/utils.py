import os
import sys
import json

import infernal


def jprint(data, load=False, marshall=True, indent=2):
    def _stringify_val(data):
        if isinstance(data, dict):
            return {k:_stringify_val(v) for k,v in data.items()}
        elif isinstance(data, list):
            return [_stringify_val(v) for v in data]
        elif isinstance(data, (str, int, float)):
            return data
        return str(data)
    _data = _stringify_val(data) if marshall else data
    try:
        _d = (
            json.dumps(json.loads(_data), indent=indent) if load else
            json.dumps(_data, indent=indent)
        )
    except:
        _d = _data
    print(_d)

def get_project_root_dir(*ext):
    path = os.path.dirname(
        os.path.abspath(__file__)
    )

    if ext:
        return os.path.abspath(os.path.join(path, *ext))
    return path


