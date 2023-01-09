from sys import stderr, stdout, exit
from os.path import isdir, join, basename, relpath, dirname, realpath
from dataclasses import dataclass, field
from argparse import ArgumentParser, Namespace
from typing import Any, AnyStr, Iterable, cast

from .build import BuilderCallbackContext
from .stream import ZipStreamWriter
from .convert import norm_path
from .constant import *


@dataclass
class Arguments(Namespace):
    dest: str = ""
    dest_stdout: bool = False
    src: Iterable[str] = field(default_factory=lambda: [])
    path: str = "/"
    comment: str = ""
    buf: int = 262144
    comp: int = COMPRESSION_STORED
    include_parent_folder: bool = True
    verbose: bool = True


@dataclass
class VerboseExra(object):
    walk: bool
    path: str
    args: Arguments


def cb_verbose(bctx: BuilderCallbackContext, extra: Any) -> None:
    """Handles pringting verbose informaton."""
    vextra = cast(VerboseExra, extra)
    fpath = bctx.path.decode()
    #path = join(vextra.path, fpath) if vextra.walk else vextra.path

    if not bctx.done or bctx.is_folder:
        print(" adding", fpath, file=stderr, end="", flush=True)
    elif bctx.done and bctx.ctx:
        cctx = bctx.ctx.compressor_ctx
        compressed = bctx.ctx.compression != 0

        if compressed:
            ratio = int((cctx.compressed_size / cctx.uncompressed_size)
                        * 100) if cctx.uncompressed_size > 0 else 100
            print(f" (compressed size {ratio}%)", file=stderr)
        else:
            print(f" (stored)", file=stderr)


def main(args: Arguments) -> None:
    """Builds zip file with given arguments."""
    out_file = stdout.buffer if args.dest_stdout else open(args.dest, "wb")

    with out_file, ZipStreamWriter(out_file, args.buf) as zsw:
        # Absolute path
        out_file_abs = realpath(out_file.name)

        # Write srcs
        for src_file in args.src:
            try:
                # Absolute path
                src_file_abs = realpath(src_file)

                if isdir(src_file):
                    # Filename in zip
                    dname = (
                        basename(relpath(src_file_abs))
                        if args.include_parent_folder else
                        ""
                    )

                    # File in dir
                    # Skip trying to add self to zip file
                    out_file_in_dir = src_file_abs == dirname(out_file_abs)
                    out_file_in_dir_path = norm_path(
                        join(args.path, basename(out_file_abs))
                        if out_file_in_dir else
                        "", False
                    )

                    # Ignore self
                    def ignore_self(path: AnyStr, ext: AnyStr, folder: bool) -> bool:
                        return out_file_in_dir and path == out_file_in_dir_path

                    # Verbose
                    if args.verbose:
                        zsw.builder.set_callback(
                            cb_verbose, VerboseExra(walk=True, path=src_file_abs, args=args))

                    zsw.walk(src_file_abs, join(args.path, dname),
                             compression=args.comp, ignore=ignore_self)
                else:
                    # Ignore self
                    if src_file_abs == out_file_abs:
                        continue

                    # Verbose
                    if args.verbose:
                        zsw.builder.set_callback(
                            cb_verbose, VerboseExra(walk=False, path=src_file_abs, args=args))

                    zsw.add_io(join(args.path, src_file),
                               open(src_file_abs, "rb"), compression=args.comp)
            except Exception as ex:
                print(str(ex), file=stderr)

        # End
        zsw.set_comment(args.comment)


if __name__ == "__main__":
    parser = ArgumentParser(prog="zipgen")
    parser.add_argument("dest", type=str,
                        help="Destination file.")
    parser.add_argument("--dest-stdout", dest="dest_stdout", action="store_true",
                        help="Sets dest output to stdout.")
    parser.add_argument("src", metavar="N src file", type=str, nargs="+",
                        help="Source files.")
    parser.add_argument("--path", type=str, default=Arguments.path,
                        help="Internal dest folder in zip.")
    parser.add_argument("--no-ipf", dest="include_parent_folder", action="store_false",
                        help="Do not include parent folder for directories.")
    parser.add_argument("--comment", type=str, default=Arguments.comment,
                        help="Comment of the zip file.")
    parser.add_argument("--buf", type=int, default=Arguments.buf,
                        help="Read buffer size.")
    parser.add_argument("--comp", type=int, default=Arguments.comp,
                        help="Compression format. 0 = STORED, 8 = DEFLATED, 12 = BZIP2 and 14 = LZMA.")
    parser.add_argument("-q", dest="verbose", action="store_false",
                        help="Sets verbose mode off.")

    parser.set_defaults(include_parent_folder=Arguments.include_parent_folder)
    parser.set_defaults(dest_stdout=Arguments.dest_stdout)
    parser.set_defaults(verbose=Arguments.verbose)

    try:
        namespace = Arguments()
        args = parser.parse_args(namespace=namespace)
        main(args)
    except Exception as ex:
        print(str(ex), file=stderr)
        exit(1)
