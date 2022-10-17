from asyncio import subprocess
from unittest import IsolatedAsyncioTestCase, main
from io import BytesIO
from zipfile import ZipFile
from zipgen import ZipBuilder


class TestSync(IsolatedAsyncioTestCase):
    async def test_stream_async(self) -> None:
        """Test stream generator."""
        builder = ZipBuilder()
        io = BytesIO()
        args = b"hello world"

        # Read process content to zip
        proc = await subprocess.create_subprocess_exec(
            "echo", args,
            stdout=subprocess.PIPE,
        )

        if proc.stdout is not None:
            async for buf in builder.add_stream_async("echo.txt", proc.stdout):
                io.write(buf)

        # End
        io.write(builder.end())

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
        builder = ZipBuilder()
        io = BytesIO()

        # Walk tests files
        async for buf in builder.walk_async("./", "/"):
            io.write(buf)

        # End
        io.write(builder.end())

        # Check existence
        with ZipFile(io, "r") as file:
            self.assertEqual(
                file.namelist(),
                ["test_sync.py", "test_async.py"],
            )

            for name in file.namelist():
                self.assertNotEqual(len(file.read(name)), 0)


if __name__ == "__main__":
    main()
