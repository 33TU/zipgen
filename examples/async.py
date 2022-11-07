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
