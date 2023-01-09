from asyncio import StreamReader
from os import name
from io import BufferedIOBase, RawIOBase

try:
    from typing import AnyStr, Awaitable, Optional, Generator, AsyncGenerator, Union, cast
    from typing import Protocol, runtime_checkable  # >= Python 3.8
except ImportError:
    from typing_extensions import Protocol, runtime_checkable  # type: ignore

from .build import *
from .constant import *


__all__ = (
    "StreamWriter",
    "ZipStreamWriter",
)


@runtime_checkable
class StreamWriter(Protocol):
    def write(self, data: bytes) -> Union[int, None]:
        ...


@runtime_checkable
class AsyncStreamWriter(Protocol):
    def write(self, data: bytes) -> Union[int, None]:
        ...

    def drain(self) -> Awaitable[None]:
        ...


class ZipStreamWriter(object):
    __slots__ = (
        "stream",
        "builder",
        "drain",
        "comment",
    )

    def __init__(self, stream: Union[StreamWriter, AsyncStreamWriter], buffer_size=65536, system=get_version_system(name)) -> None:
        self.stream = stream
        self.builder = ZipBuilder(buffer_size, system)
        self.comment: Union[bytes, str, bytearray, None] = None
        self.drain = (
            cast(AsyncStreamWriter, self.stream).drain
            if isinstance(stream, AsyncStreamWriter) else
            None
        )

    def __enter__(self) -> 'ZipStreamWriter':
        return self

    async def __aenter__(self) -> 'ZipStreamWriter':
        return self

    def __exit__(self, *_) -> None:
        self.end()

    async def __aexit__(self, *_) -> None:
        await self.end_async()

    def set_comment(self, comment: AnyStr) -> None:
        """Sets comment for the zip. Applied on end."""
        self.comment = comment

    def add_folder(self, path: AnyStr, utc_time: Optional[float] = None, comment: AnyStr = None) -> None:
        """Writes the folder to the stream."""
        buf = self.builder.add_folder(path, utc_time, comment)
        self.stream.write(buf)

    def add_buf(self, path: AnyStr, buf: Union[bytes, bytearray, memoryview], utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> None:
        """Writes the buf to the stream."""
        for buf in self.builder.add_buf(path, buf, utc_time, compression, comment):
            self.stream.write(buf)

    def add_gen(self, path: AnyStr, gen: Generator[bytes, None, None], utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> None:
        """Writes the generator to the stream."""
        for buf in self.builder.add_gen(path, gen, utc_time, compression, comment):
            self.stream.write(buf)

    def add_io(self, path: AnyStr, io: Union[BufferedIOBase, RawIOBase], utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> None:
        """Writes the io to the stream."""
        for buf in self.builder.add_io(path, io, utc_time, compression, comment):
            self.stream.write(buf)

    def walk(self, src: AnyStr, dest: AnyStr, utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment: AnyStr = None,
             ignore: Optional[WalkIgnoreCallable] = walk_ignore_default, no_compress: Optional[WalkNoCompressCallable] = walk_no_compress_default) -> None:
        """Generates the file headers and contents from src directory."""
        for buf in self.builder.walk(src, dest, utc_time, compression, comment, ignore, no_compress):
            self.stream.write(buf)

    def end(self, comment: AnyStr = None) -> None:
        """Writes EOCD which contains headers for all added files."""
        buf = self.builder.end(comment or cast(AnyStr, self.comment))
        self.stream.write(buf)

    async def add_folder_async(self, path: AnyStr, utc_time: Optional[float] = None, comment: AnyStr = None) -> None:
        """Writes the folder to the stream asyncnorously."""
        buf = self.builder.add_folder(path, utc_time, comment)
        self.stream.write(buf)

        if self.drain is not None:
            await self.drain()

    async def add_buf_async(self, path: AnyStr, buf: Union[bytes, bytearray, memoryview], utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> None:
        """Writes the buf to the stream."""
        for buf in self.builder.add_buf(path, buf, utc_time, compression, comment):
            self.stream.write(buf)

            if self.drain is not None:
                await self.drain()

    async def add_gen_async(self, path: AnyStr, gen: AsyncGenerator[bytes, None], utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> None:
        """Writes the generator to the stream asyncnorously."""
        async for buf in self.builder.add_gen_async(path, gen, utc_time, compression, comment):
            self.stream.write(buf)

            if self.drain is not None:
                await self.drain()

    async def add_io_async(self, path: AnyStr, io: Union[BufferedIOBase, RawIOBase], utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> None:
        """Writes the file to the stream asyncnorously."""
        async for buf in self.builder.add_io_async(path, io, utc_time, compression, comment):
            self.stream.write(buf)

            if self.drain is not None:
                await self.drain()

    async def add_stream_async(self, path: AnyStr, reader: StreamReader, utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="", buf_size=4096) -> None:
        """Writes the stream to the stream asyncnorously."""
        async for buf in self.builder.add_stream_async(path, reader, utc_time, compression, comment):
            self.stream.write(buf)

            if self.drain is not None:
                await self.drain()

    async def walk_async(self, src: AnyStr, dest: AnyStr, utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment: AnyStr = None,
                         ignore: Optional[WalkIgnoreCallable] = walk_ignore_default, no_compress: Optional[WalkNoCompressCallable] = walk_no_compress_default) -> None:
        """Generates the file headers and contents from src directory asyncnorously asyncnorously."""
        async for buf in self.builder.walk_async(src, dest, utc_time, compression, comment, ignore, no_compress):
            self.stream.write(buf)

            if self.drain is not None:
                await self.drain()

    async def end_async(self, comment: AnyStr = None) -> None:
        """Writes EOCD which contains headers for all added files asyncnorously."""
        buf = self.builder.end(comment or cast(AnyStr, self.comment))
        self.stream.write(buf)

        if self.drain is not None:
            await self.drain()
