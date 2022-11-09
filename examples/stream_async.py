import asyncio
import zipgen


async def create_async() -> None:
    # Async methods end with suffix _async
    # ZipStreamWriter supports regular Streams and asyncio.StreamWriter
    # If stream provides awaitable .drain() method such as asyncio.StreamWriter, it will be awaited after each write.

    # Dot not call ZipStreamWriter.end() if with clause is used
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
