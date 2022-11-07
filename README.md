# zipgen

Zipgen is a simple and performant zip archive generator for Python 3.7 and
later. It supports ZIP64, uncompressed and various compression formats such as:
Deflated, Bzip and LZMA.

Zipgen supports synchronous asynchronous generation. Zipgen can zip archives on
the fly from stream objects such as FileIO, BytesIO, Generators and Async
StreamReader.

Zipgen also supports recursive creation of zip archives from existing folders
synchronously or asynchronously.

## Command

Zipgen can also be used as a command:
`python -m zipgen dest.zip file1.txt ./any/folder`.

The command supports adding several files or folders at once recursively.
Compression method can be set with `--comp` option and comment can be set with
`--comment`.

# Install

`python -m pip install zipgen`

---

## Sync example

```py
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
```

## Async example

```py
import asyncio
import zipgen
from typing import AsyncGenerator


async def main() -> None:
    """Creates dist_async.zip asynchronously."""
    builder = zipgen.ZipBuilder()

    with open("dist_async.zip", "wb+") as file:
        # Add file, default compression is COMPRESSION_STORED
        async for buf in builder.add_io_async("async.py", open("async.py", "rb")):
            file.write(buf)

        # Walk src
        async for buf in builder.walk_async("../src", "src-files-dist", compression=zipgen.COMPRESSION_DEFLATED):
            file.write(buf)

        # Add from AsyncGenerator
        async def data_gen_async() -> AsyncGenerator[bytes, None]:
            for i in range(1024):
                await asyncio.sleep(0)
                yield f"hello from async generator {i}\n".encode()

        async for buf in builder.add_gen_async("generator.txt", data_gen_async(), compression=zipgen.COMPRESSION_LZMA):
            file.write(buf)

        # Read process content to zip
        proc = await asyncio.subprocess.create_subprocess_exec(
            "dir",
            stdout=asyncio.subprocess.PIPE,
        )

        if proc.stdout is not None:
            async for buf in builder.add_stream_async("dir.txt", proc.stdout, compression=zipgen.COMPRESSION_LZMA):
                file.write(buf)

        # End
        file.write(builder.end("This is a comment for async.py example."))


if __name__ == "__main__":
    asyncio.run(main())
```
