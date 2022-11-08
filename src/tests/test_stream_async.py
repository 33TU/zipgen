from asyncio import subprocess, sleep
from typing import AsyncGenerator
from unittest import IsolatedAsyncioTestCase, main
from io import BytesIO
from sys import argv
from os import listdir
from os.path import dirname
from zipfile import ZipFile
from zipgen import ZipStreamWriter


class TestAsyncStream(IsolatedAsyncioTestCase):
    async def test_stream_async(self) -> None:
        """Test stream generator."""
        io = BytesIO()
        args = b"hello world"

        with ZipStreamWriter(io) as stream:
            # Read process content to zip
            proc = await subprocess.create_subprocess_exec(
                "echo", args,
                stdout=subprocess.PIPE,
            )

            if proc.stdout is not None:
                await stream.add_stream_async("echo.txt", proc.stdout)

        # Check existence
        with ZipFile(io, "r") as file:
            self.assertEqual(
                file.namelist(),
                ["echo.txt"],
            )

            for name in file.namelist():
                self.assertTrue(file.read(name).startswith(args))

    async def test_walk_async(self) -> None:
        """Test walk generator."""
        io = BytesIO()
        path = dirname(argv[0])

        with ZipStreamWriter(io) as stream:
            # Walk tests files
            await stream.walk_async(path, "/")

        # Check existence
        with ZipFile(io, "r") as file:
            self.assertEqual(
                file.namelist(),
                listdir(path),
            )

            for name in file.namelist():
                self.assertNotEqual(len(file.read(name)), 0)

    async def test_gen_async(self) -> None:
        """Test async generator."""
        io = BytesIO()

        # Contents for AsyncGenerator
        data = (b"hello", b"world", b"from", b"AsyncGenerator", b"x"*1024)

        with ZipStreamWriter(io) as stream:
            # AsyncGenerator for data
            async def gen_data_async() -> AsyncGenerator[bytes, None]:
                for buf in data:
                    await sleep(0)
                    yield buf

            # Write generator content to io
            await stream.add_gen_async("gen.txt", gen_data_async())

        # Check existence
        with ZipFile(io, "r") as file:
            self.assertEqual(
                file.namelist(),
                ["gen.txt"],
            )

            for name in file.namelist():
                self.assertEqual(file.read(name), b"".join(data))


if __name__ == "__main__":
    main()
