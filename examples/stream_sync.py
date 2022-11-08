import io
import zipgen


def create_sync() -> None:
    # ZipStreamWriter provides more practical interface using ZipBuilder
    # And it has has all the methods from ZipBuilder.

    # Dot not call ZipStreamWriter.end() if with clause is used
    with (
            open("stream_sync.zip", "wb+") as f,
            zipgen.ZipStreamWriter(f) as zsw,
    ):
        # Add folders, library corrects path to correct format
        zsw.add_folder("hello/world")
        zsw.add_folder("hello/from/stream")
        zsw.add_folder("//hello\\from//path/correcting")
        # => hello/from/path/correcting

        # Add three buffers, default compression is COMPRESSION_STORED
        zsw.add_buf("buf/buf1.txt", b"hello from buf1!")
        zsw.add_buf("buf/buf2.txt", bytearray(b"hello from buf2!"))
        zsw.add_buf("buf/buf3.txt", memoryview(b"hello from buf3!"))

        # Add self
        zsw.add_io("self.py", open(__file__, "rb"),
                   compression=zipgen.COMPRESSION_DEFLATED)

        # Add BytesIO
        zsw.add_io("BytesIO.txt", io.BytesIO(b"hello from BytesIO!"),
                   compression=zipgen.COMPRESSION_BZIP2)

        # Add generator
        def data_gen():
            for i in range(1, 100):
                yield f"hello from line {i}\n".encode()

        zsw.add_gen("generator.txt", data_gen(),
                    compression=zipgen.COMPRESSION_LZMA)

        # Walk files
        zsw.walk("../src", "zipgen/src",
                 compression=zipgen.COMPRESSION_DEFLATED)

        # Set comment
        zsw.set_comment("created by stream_sync.py")


if __name__ == '__main__':
    create_sync()
