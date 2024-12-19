"""Optimized json parsing"""

import json
import re
from typing import TextIO


def parse_fast(fileobj: TextIO) -> dict:
    """Optimized parsing to get just timestamps from files.

    Falls back to json.load() when a parsing error occurs.
    """
    PREFIX_LEN = 256
    match = re.match(r"\{\"first_ts\":(\d+),\"last_ts\":(\d+)", fileobj.read(PREFIX_LEN))
    try:
        if match:
            return {"first_ts": int(match.group(1)), "last_ts": int(match.group(2))}
    except IndexError:
        pass

    fileobj.seek(0)
    return json.load(fileobj)
