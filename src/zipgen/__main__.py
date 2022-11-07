from sys import stderr, exit
from os.path import isdir
from dataclasses import dataclass, field
from argparse import ArgumentParser, Namespace
from typing import Iterable

from .build import ZipBuilder
from .constant import *


@dataclass
class Arguments(Namespace):
    dest: str = ""
    src: Iterable[str] = field(default_factory=lambda: [])
    path: str = "/"
    comment: str = ""
    buf: int = 65536
    comp: int = COMPRESSION_STORED


def main(args: Arguments) -> None:
    """Builds zip file with given arguments."""
    builder = ZipBuilder(args.buf)

    with open(args.dest, "wb+") as file:
        # Write srcs
        for fname in args.src:
            try:
                if isdir(fname):
                    for buf in builder.walk(fname, args.path, compression=args.comp):
                        file.write(buf)
                else:
                    for buf in builder.add_io(fname, open(fname, "rb"), compression=args.comp):
                        file.write(buf)
            except Exception as ex:
                print(str(ex), file=stderr)

        # End
        file.write(builder.end(args.comment))


if __name__ == "__main__":
    parser = ArgumentParser(prog="zipgen")
    parser.add_argument("dest", type=str,
                        help="Destination file.")
    parser.add_argument("src", metavar="N src file", type=str, nargs="+",
                        help="Source files.")
    parser.add_argument("--path", type=str, default=Arguments.path,
                        help="Internal dest folder in zip.")
    parser.add_argument("--comment", type=str, default=Arguments.comment,
                        help="Comment of the zip file.")
    parser.add_argument("--buf", type=int, default=Arguments.buf,
                        help="Read buffer size.")
    parser.add_argument("--comp", type=int, default=Arguments.comp,
                        help="Compression format. 0 = STORED, 8 = DEFLATED, 12 = BZIP2 and 14 = LZMA.")

    try:
        namespace = Arguments()
        args = parser.parse_args(namespace=namespace)
        main(args)
    except Exception as ex:
        print(str(ex), file=stderr)
        exit(1)
