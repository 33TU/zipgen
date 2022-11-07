from time import localtime
from posixpath import normpath
from typing import Tuple, Optional, AnyStr


__all__ = (
    "dos_time",
    "norm_path",
)


def dos_time(utc_time: Optional[float] = None) -> Tuple[int, int]:
    """Converts UTC timestamp to DOS time and date."""
    stime = localtime(utc_time)
    time = (stime[3] << 11 | stime[4] << 5 | (stime[5] // 2)) & 0xffff
    date = ((stime[0] - 1980) << 9 | stime[1] << 5 | stime[2]) & 0xffff

    return (time, date,)


def norm_path(path: AnyStr, folder: bool) -> bytes:
    """Converts path by normalizing it for a file or a folder. Path must be UTF-8 encoded bytes or str."""
    if isinstance(path, str):
        path_bytes = path.encode("utf8")
    elif isinstance(path, (bytes, bytearray,)):
        path_bytes = path
    else:
        raise ValueError("Path has to be bytes or str.")

    path_bytes = path_bytes.replace(b"\\", b"/")
    path_bytes = normpath(path_bytes)
    path_bytes = path_bytes.lstrip(b"/")

    if folder and not path_bytes.endswith(b"/"):
        path_bytes = path_bytes + b"/"

    return path_bytes
