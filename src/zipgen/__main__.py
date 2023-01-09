from sys import stderr, stdout, exit
from os import stat, stat_result
from os.path import isdir, join, basename, abspath, dirname, relpath, splitext
from dataclasses import dataclass, field
from argparse import ArgumentParser, Namespace
from typing import Any, AnyStr, Iterable, cast

from .build import BuilderCallableContext, walk_no_compress_default
from .stream import ZipStreamWriter
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
    path: str
    walk: bool = False
    cwd: bool = False


def cb_verbose(bctx: BuilderCallableContext, extra: Any) -> None:
    """Handles pringting verbose informaton."""
    vextra = cast(VerboseExra, extra)
    fpath = bctx.path.decode()

    # Get path
    if vextra.walk:
        path = join(
            vextra.path if vextra.cwd else dirname(vextra.path),
            fpath,
        )
    else:
        path = vextra.path

    if not bctx.done:
        print(" adding", path, file=stderr, end="", flush=True)
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
        out_file_abs = abspath(out_file.name)
        cwd_abs = abspath(".")

        # Write srcs
        for src_file in args.src:
            try:
                # Absolute path
                src_file_abs = abspath(src_file)

                if isdir(src_file):
                    # Filename in zip
                    dname = (
                        basename(relpath(src_file_abs))
                        if args.include_parent_folder else
                        ""
                    )

                    # Ignore self
                    def ignore_self(path: AnyStr, ext: AnyStr, folder: bool, stat: stat_result) -> bool:
                        return path == out_file_abs

                    # Verbose
                    if args.verbose:
                        zsw.builder.set_callback(
                            cb_verbose, VerboseExra(path=src_file_abs, walk=True, cwd=cwd_abs == src_file_abs))

                    # Add files to stream
                    zsw.walk(src_file_abs, join(args.path, dname),
                             compression=args.comp, ignore=ignore_self)
                else:
                    # Ignore self
                    if src_file_abs == out_file_abs:
                        continue

                    # Verbose
                    if args.verbose:
                        zsw.builder.set_callback(
                            cb_verbose, VerboseExra(path=src_file_abs))

                    # Check if file needs to be compressed
                    ext = splitext(src_file_abs)[1].lower()
                    file_compression = (
                        COMPRESSION_STORED
                        if walk_no_compress_default(src_file_abs, ext, stat(src_file_abs)) else
                        args.comp
                    )

                    # Add file to stream
                    zsw.add_io(join(args.path, src_file),
                               open(src_file_abs, "rb"), compression=file_compression)
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
