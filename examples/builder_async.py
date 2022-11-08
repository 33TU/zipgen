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
