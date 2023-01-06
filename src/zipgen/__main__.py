from sys import stderr, exit
from os.path import isdir, join, basename, relpath, dirname, abspath
from dataclasses import dataclass, field
from argparse import ArgumentParser, Namespace
from typing import AnyStr, Iterable

from .stream import ZipStreamWriter
from .convert import norm_path
from .constant import *


@dataclass
class Arguments(Namespace):
    dest: str = ""
    src: Iterable[str] = field(default_factory=lambda: [])
    path: str = "/"
    comment: str = ""
    buf: int = 262144
    comp: int = COMPRESSION_STORED
    include_parent_folder: bool = True


def main(args: Arguments) -> None:
    """Builds zip file with given arguments."""
    with open(args.dest, "wb") as file, ZipStreamWriter(file, args.buf) as zsw:
        # File path
        fpath = abspath(file.name)

        # Write srcs
        for fname in args.src:
            try:
                if isdir(fname):
                    # Filename in zip
                    dname = (
                        basename(relpath(fname))
                        if args.include_parent_folder else
                        ""
                    )

                    # File in dir
                    # Skip trying to add self to zip file
                    file_in_dir = abspath(fname) == dirname(fpath)
                    file_in_dir_path = norm_path(
                        join(args.path, basename(file.name))
                        if file_in_dir else
                        "", False
                    )

                    # Ignore self
                    def ignore_self(path: AnyStr, ext: AnyStr, folder: bool) -> bool:
                        return file_in_dir and path == file_in_dir_path

                    zsw.walk(fname, join(args.path, dname),
                             compression=args.comp, ignore=ignore_self)
                else:
                    zsw.add_io(join(args.path, fname),
                               open(fname, "rb"), compression=args.comp)
            except Exception as ex:
                print(str(ex), file=stderr)

        # End
        zsw.set_comment(args.comment)


if __name__ == "__main__":
    parser = ArgumentParser(prog="zipgen")
    parser.add_argument("dest", type=str,
                        help="Destination file.")
    parser.add_argument("src", metavar="N src file", type=str, nargs="+",
                        help="Source files.")
    parser.add_argument("--path", type=str, default=Arguments.path,
                        help="Internal dest folder in zip.")
    parser.add_argument("--no-ipf", dest="include_parent_folder", action='store_false',
                        help="Do not include parent folder for directories.")
    parser.add_argument("--comment", type=str, default=Arguments.comment,
                        help="Comment of the zip file.")
    parser.add_argument("--buf", type=int, default=Arguments.buf,
                        help="Read buffer size.")
    parser.add_argument("--comp", type=int, default=Arguments.comp,
                        help="Compression format. 0 = STORED, 8 = DEFLATED, 12 = BZIP2 and 14 = LZMA.")

    parser.set_defaults(include_parent_folder=Arguments.include_parent_folder)

    try:
        namespace = Arguments()
        args = parser.parse_args(namespace=namespace)
        main(args)
    except Exception as ex:
        print(str(ex), file=stderr)
        exit(1)
