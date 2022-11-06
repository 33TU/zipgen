# zipgen

Zipgen is a simple and performant zip archive generator for Python 3.7 and
later. It supports ZIP64, uncompressed and various compression formats such as:
Deflated, Bzip and LZMA.

Zipgen supports synchronous asynchronous generation. Zipgen can zip archives on
the fly from stream objects such as FileIO, BytesIO and Async StreamReader.

Zipgen also supports recursive creation of zip archives from existing folders
synchronously or asynchronously.

## Command

Zipgen can also be used as a command:
`python -m zipgen dest.zip file1.txt ./any/folder`.

The command supports adding several files or folders at once recursively.
Compression method can be set with `--comp` option and comment can be set with
`--comment`.

---

## Sync example

```py
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
```

## Async example

```py
import asyncio
import zipgen


async def main() -> None:
    """Creates dist_async.zip asynchronously."""
    builder = zipgen.ZipBuilder()

    with open("dist_async.zip", "wb+") as file:
        # Add file, default compression is COMPRESSION_STORED
        async for buf in builder.add_file_async("async.py", open("async.py", "rb")):
            file.write(buf)

        # Walk src
        async for buf in builder.walk_async("../src", "src-files-dist", compression=zipgen.COMPRESSION_DEFLATED):
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
