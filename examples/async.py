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
