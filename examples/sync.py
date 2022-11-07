import io
import zipgen
from typing import Generator


def main() -> None:
    """Creates dist_sync.zip synchronously."""
    builder = zipgen.ZipBuilder()

    with open("dist_sync.zip", "wb+") as file:
        # Add file, default compression is COMPRESSION_STORED
        for buf in builder.add_io("async.py", open("sync.py", "rb")):
            file.write(buf)

        # Add from BytesIO
        for buf in builder.add_io("buffer.txt", io.BytesIO(b"Hello world from BytesIO!"), compression=zipgen.COMPRESSION_BZIP2):
            file.write(buf)

        # Walk src
        for buf in builder.walk("../src", "src-files-dist", compression=zipgen.COMPRESSION_DEFLATED):
            file.write(buf)

        # Add from Generator
        def data_gen() -> Generator[bytes, None, None]:
            for i in range(1024):
                yield f"hello from generator {i}\n".encode()

        for buf in builder.add_gen("generator.txt", data_gen(), compression=zipgen.COMPRESSION_LZMA):
            file.write(buf)

        # Add empty folders
        file.write(builder.add_folder("empty/folder/it/is"))
        # its OK to start path with / or \, library corrects everything.
        file.write(builder.add_folder("/empty/folder/indeed"))

        # End
        file.write(builder.end("This is a comment for sync.py example."))


if __name__ == "__main__":
    main()
