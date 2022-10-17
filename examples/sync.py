import io
import zipgen


def main() -> None:
    """Creates dist_sync.zip synchronously."""
    builder = zipgen.ZipBuilder()

    with open("dist_sync.zip", "wb+") as file:
        # Add file, default compression is COMPRESSION_STORED
        for buf in builder.add_file("async.py", open("sync.py", "rb")):
            file.write(buf)

        # Add BytesIO
        for buf in builder.add_file("buffer.txt", io.BytesIO(b"Hell world from BytesIO!"), compression=zipgen.COMPRESSION_BZIP2):
            file.write(buf)

        # Walk src
        for buf in builder.walk("../src", "src-files-dist", compression=zipgen.COMPRESSION_DEFLATED):
            file.write(buf)

        # Add empty folders
        file.write(builder.add_folder("empty/folder/it/is"))
        # its OK to start path with / or \, library corrects everything.
        file.write(builder.add_folder("/empty/folder/indeed"))

        # End
        file.write(builder.end("This is a comment for sync.py example."))


if __name__ == "__main__":
    main()
