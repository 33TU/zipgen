# zipgen

Zipgen is a simple and performant zip archive generator for Python 3.7 and
later. It supports ZIP64, uncompressed and various compression formats such as:
Deflated, Bzip and LZMA.

Zipgen supports synchronous asynchronous generation. Zipgen can zip archives
from stream objects such as FileIO, BytesIO, generators and asynchronous
StreamReader.

Zipgen also supports recursive creation of zip archives from existing folders.
Synchronously or asynchronously.

Zip archives can be created using the ZipBuilder and ZipStreamWriter classes.
ZipBuilder provides methods that return byte generators.

The ZipStreamWriter class can be used to write directly to streams and to
asynchronous streams, which provide a wait drain() method, such as
asyncio.StreamWriter. ZipStreamWriter uses ZipBuilder internally providing all
of the same methods.

## Command

Zipgen can also be used as a command:
`python -m zipgen dest.zip file1.txt ./any/folder`.

The command supports adding several files or folders at once recursively.
Compression method can be set with `--comp` option and comment can be set with
`--comment`.

# Install

`python -m pip install zipgen`

---

## Sync ZipStreamWriter Example

```py
import io
import zipgen


def create_sync() -> None:
    # ZipStreamWriter provides more practical interface using ZipBuilder
    # And it has has all the methods from ZipBuilder.

    # Do not call ZipStreamWriter.end() if with clause is used
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
```

## Async ZipStreamWriter Example

```py
import asyncio
import zipgen


async def create_async() -> None:
    # Async methods end with suffix _async
    # ZipStreamWriter supports regular Streams and asyncio.StreamWriter
    # If stream provides awaitable .drain() method such as asyncio.StreamWriter, it will be awaited after each write.

    # Do not call ZipStreamWriter.end() if with clause is used
    with (
            open("stream_async.zip", "wb+") as f,
            zipgen.ZipStreamWriter(f) as zsw,
    ):
        # Add folders, library corrects path to correct format
        await zsw.add_folder_async("hello/world")
        await zsw.add_folder_async("hello/from/stream")
        await zsw.add_folder_async("//hello\\from//path/correcting")
        # => hello/from/path/correcting

        # Add self
        await zsw.add_io_async("self.py", open(__file__, "rb"),
                               compression=zipgen.COMPRESSION_DEFLATED)

        # Add async generator
        async def data_gen():
            for i in range(1, 100):
                await asyncio.sleep(0)
                yield f"hello from line {i}\n".encode()

        await zsw.add_gen_async("generator.txt", data_gen(),
                                compression=zipgen.COMPRESSION_LZMA)

        # Walk files
        await zsw.walk_async("../src", "zipgen/src", compression=zipgen.COMPRESSION_DEFLATED)

        # Pipe process stdout
        proc = await asyncio.subprocess.create_subprocess_exec(
            "echo", "hello from subprocess",
            stdout=asyncio.subprocess.PIPE,
        )

        if proc.stdout is not None:
            await zsw.add_stream_async("echo.txt", proc.stdout)

        # Set comment
        zsw.set_comment("created by stream_async.py")


if __name__ == '__main__':
    asyncio.run(create_async())
```

## Sync ZipBuilder Example

```py
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
```

## Async ZipBuilder Example

```py
import asyncio
import zipgen


async def create_async() -> None:
    # Creates builder_sync.zip asynchronously using ZipBuilder.
    # For synchronous methods use methods withour "_async" suffix.

    b = zipgen.ZipBuilder()

    with open("builder_async.zip", "wb+") as file:
        # Add self
        async for buf in b.add_io_async("self.py", open(__file__, "rb"),
                                        compression=zipgen.COMPRESSION_DEFLATED):
            file.write(buf)

        # Add async generator
        async def data_gen():
            for i in range(1, 100):
                await asyncio.sleep(0)
                yield f"hello from line {i}\n".encode()

        async for buf in b.add_gen_async("generator.txt", data_gen(),
                                         compression=zipgen.COMPRESSION_LZMA):
            file.write(buf)

        # Walk files
        async for buf in b.walk_async("../src", "zipgen/src", compression=zipgen.COMPRESSION_DEFLATED):
            file.write(buf)

        # Pipe process stdout
        proc = await asyncio.subprocess.create_subprocess_exec(
            "echo", "hello from subprocess",
            stdout=asyncio.subprocess.PIPE,
        )

        if proc.stdout is not None:
            async for buf in b.add_stream_async("echo.txt", proc.stdout):
                file.write(buf)

        # Set comment
        file.write(b.end("created by builder_async.py"))


if __name__ == '__main__':
    asyncio.run(create_async())
```
