from time import localtime, struct_time
from os.path import normpath
from typing import Tuple, Union, Optional


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


def norm_path(path: Union[str, bytes], folder: bool) -> bytes:
    """Converts path by normalizing it for a file or a folder. Path must be UTF-8 encoded bytes or str."""
    if isinstance(path, str):
        path = path.encode("utf8")

    path = path.replace(b"\\", b"/")
    path = normpath(path)
    path = path.lstrip(b"/")

    if folder and not path.endswith(b"/"):
        path = path + b"/"

    return path
