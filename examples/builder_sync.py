import io
import zipgen


def create_sync() -> None:
    # Creates builder_sync.zip synchronously using ZipBuilder.
    # For asynchronous methods use methods with "_async" suffix.

    b = zipgen.ZipBuilder()

    with open("builder_sync.zip", "wb+") as file:
        # Add folders, library corrects path to correct format
        file.write(b.add_folder("hello/world"))
        file.write(b.add_folder("hello/from/stream"))
        file.write(b.add_folder("//hello\\from//path/correcting"))
        # => hello/from/path/correcting

        # Add three buffers, default compression is COMPRESSION_STORED
        for buf in b.add_buf("buf/buf1.txt", b"hello from buf1!"):
            file.write(buf)

        for buf in b.add_buf("buf/buf2.txt", bytearray(b"hello from buf2!")):
            file.write(buf)

        for buf in b.add_buf("buf/buf3.txt", memoryview(b"hello from buf3!")):
            file.write(buf)

        # Add self
        for buf in b.add_io("self.py", open(__file__, "rb"),
                            compression=zipgen.COMPRESSION_DEFLATED):
            file.write(buf)

        # Add BytesIO
        for buf in b.add_io("BytesIO.txt", io.BytesIO(b"hello from BytesIO!"),
                            compression=zipgen.COMPRESSION_BZIP2):
            file.write(buf)

        # Add generator
        def data_gen():
            for i in range(1, 100):
                yield f"hello from line {i}\n".encode()

        for buf in b.add_gen("generator.txt", data_gen(),
                             compression=zipgen.COMPRESSION_LZMA):
            file.write(buf)

        # Walk files
        for buf in b.walk("../src", "zipgen/src",
                          compression=zipgen.COMPRESSION_DEFLATED):
            file.write(buf)

        # Set comment
        file.write(b.end("created by builder_sync.py"))


if __name__ == "__main__":
    create_sync()
