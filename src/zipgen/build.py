from dataclasses import dataclass
from io import BufferedIOBase, BufferedReader
from os import name, stat, walk
from os.path import relpath, join, splitext
from typing import AnyStr, Dict, AsyncGenerator, Generator, Tuple, Union, Optional

from .compress import *
from .constant import *
from .convert import *
from .pack import *


__all__ = (
    "version_made_by",
    "ZipContext",
    "ZipBuilder",
)


def version_made_by(name: str) -> int:
    """Returns version integer for current OS:"""
    return MADE_BY_WINDOWS if name == "nt" else MADE_BY_UNIX


@dataclass
class ZipContext(object):
    path: bytes
    io: BufferedIOBase
    compression: int
    compressor: CompressorBase
    compressor_ctx: CompressorContext
    flag: int
    time: int
    date: int
    version: int
    external_attributes: int
    comment: bytes
    relative_offset: int


class ZipBuilder(object):
    __slots__ = (
        "buffer",
        "version_made",
        "version_extract",
        "headers",
        "ctx",
        "offset",
    )

    def __init__(self, buffer_size=16384, version_made=version_made_by(name)) -> None:
        self.buffer = memoryview(bytearray(buffer_size))
        self.version_made = version_made
        self.version_extract = CREATE_DEFAULT
        self.headers: Dict[bytes, bytes] = {}
        self.ctx: Optional[ZipContext] = None
        self.offset = 0

    def _clear_ctx(self) -> None:
        """Clear context."""
        self.ctx = None

    def _new_file_ctx(self, path: Union[bytes, str], io: BufferedIOBase, utc_time: Optional[float], compression: int, comment: Union[bytes, str]) -> ZipContext:
        """Adds file and returns generator which yields LocalFile header and data."""
        if self.ctx is not None:
            raise ValueError("File operation pending.")

        path = norm_path(path, False)
        if path in self.headers:
            raise ValueError("Path already in headers.")

        if isinstance(comment, str):
            comment = comment.encode("utf8")

        # Try getting file stat
        file_attr: Tuple[int, Optional[float]]
        if isinstance(io, BufferedReader):
            file_stat = stat(io.fileno())
            file_attr = ((file_stat.st_mode & 0xFFFF)
                         << 16, file_stat.st_mtime,)
        else:
            file_attr = (DEFAULT_EXTERNAL_ATTR, None,)

        # External attr
        external_attr = file_attr[0]

        # Time and date
        if utc_time is None:
            utc_time = file_attr[1]
        time, date = dos_time(utc_time)

        # Extract version
        extract_version = get_extract_version(compression, False)
        if extract_version >= self.version_extract:
            self.version_extract = extract_version

        return ZipContext(
            path=path,
            io=io,
            compression=compression,
            compressor=get_compressor(compression),
            compressor_ctx=CompressorContext(),
            flag=FLAG_DEFAULT_LZMA_FILE if compression == COMPRESSION_LZMA else FLAG_DEFAULT_FILE,
            time=time,
            date=date,
            version=extract_version,
            external_attributes=external_attr,
            comment=comment,
            relative_offset=self.offset,
        )

    def _write(self, buf: bytes) -> bytes:
        """Returns buffer and increases offset by length of the buffer."""
        self.offset += len(buf)
        return buf

    def _write_local_file(self) -> bytes:
        """Returns buffer containing LocalFile header."""
        if self.ctx is None:
            raise ValueError("No current context.")

        return self._write(pack_header_with_data(HEADER_LOCAL_FILE, LocalFile(
            self.ctx.version,
            self.ctx.flag,
            self.ctx.compression,
            self.ctx.time,
            self.ctx.date,
            0,  # crc32
            0,  # compressed size
            0,  # uncompressed size
            len(self.ctx.path),
            0  # extra len
        ), self.ctx.path))

    def _write_data_descriptor(self) -> bytes:
        """Returns buffer containing DataDescriptor(64) header."""
        if self.ctx is None:
            raise ValueError("No current context.")

        use_zip64 = self.ctx.compressor_ctx.compressed_size >= INT32_MAX
        crc32 = self.ctx.compressor_ctx.crc32
        comp_size = self.ctx.compressor_ctx.compressed_size
        uncompsize = self.ctx.compressor_ctx.uncompressed_size

        if use_zip64:
            return self._write(pack_header(HEADER_DATA_DESCRIPTOR64, DataDescriptor64(crc32, comp_size, uncompsize)))
        else:
            return self._write(pack_header(HEADER_DATA_DESCRIPTOR64, DataDescriptor(crc32, comp_size, uncompsize)))

    def _write_end(self, comment: bytes) -> bytes:
        """Returns buffer containing End Of Central directory and zip64 headers if necessary."""
        try:
            buf = bytearray()
            count = len(self.headers)

            # Write all headers into bytearr
            for header in self.headers.values():
                buf += header

            # Check if offset past int32 max
            size = len(buf)
            offset = self.offset + size
            use_zip64 = offset >= INT32_MAX or count >= 0xFFFF

            # Zip64 record and locator
            if use_zip64:
                # Record
                buf += pack_header(HEADER_CENTRAL_DIRECTORY_RECORD64, CentralDirectoryRecord64(
                    SIZE_CENTRAL_DIRECTORY_RECORD64_REMAINING,
                    self.version_made,
                    self.version_extract,
                    0,  # Disk number
                    0,  # Disk start
                    count,
                    count,
                    size,
                    self.offset,
                ))

                # Locator
                buf += pack_header(HEADER_CENTRAL_DIRECTORY_LOCATOR64, CentralDirectoryLocator64(
                    0,  # Disk number
                    offset,
                    1,  # Total disks
                ))

            # End of Central Directory
            buf += pack_header_with_data(HEADER_END_OF_CENTRAL_DIRECTORY, EndOfCentralDirectory(
                0,  # Disk number
                0,  # Disk start
                0xFFFF if use_zip64 else count,
                0xFFFF if use_zip64 else count,
                0xFFFFFFFF if use_zip64 else size,
                0xFFFFFFFF if use_zip64 else self.offset,
                len(comment),
            ), comment)

            return bytes(buf)
        finally:
            # Reset
            self.offset = 0
            self.headers.clear()

    def _set_header(self) -> None:
        """Sets headers key to context"s path which point to CentralDirectory bytes."""
        if self.ctx is None:
            raise ValueError("No current context.")

        cctx = self.ctx.compressor_ctx
        use_zip64 = cctx.compressed_size >= INT32_MAX or self.ctx.relative_offset >= INT32_MAX

        # Extended information for zip64
        extra = pack_header(TAG_EXTENDED_INFORMATION64, ExtendedInformation64(
            SIZE_EXTENDED_INFORMATION,  # Size of extended information.
            cctx.uncompressed_size,
            cctx.compressed_size,
            self.ctx.relative_offset,
            0,  # Disk start number
        )) if use_zip64 else b""

        # Store header bytes.
        self.headers[self.ctx.path] = pack_header_with_data(HEADER_CENTRAL_DIRECTORY, CentralDirectory(
            self.version_made,
            self.ctx.version,
            self.ctx.flag,
            self.ctx.compression,
            self.ctx.time,
            self.ctx.date,
            cctx.crc32,
            0xFFFFFFFF if use_zip64 else cctx.compressed_size,
            0xFFFFFFFF if use_zip64 else cctx.uncompressed_size,
            len(self.ctx.path),
            len(extra),
            len(self.ctx.comment),
            0,  # Disk start
            0,  # Internal Attributes
            self.ctx.external_attributes,
            0xFFFFFFFF if use_zip64 else self.ctx.relative_offset,
        ), self.ctx.path, extra, self.ctx.comment)

    def add_file(self, path: Union[bytes, str], io: BufferedIOBase, utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> Generator[bytes, None, None]:
        """Adds file and returns Generator object."""
        with io:
            # Create file context.
            self.ctx = self._new_file_ctx(
                path, io, utc_time, compression, comment
            )

            # Yield file's header and content.
            try:
                yield self._write_local_file()

                for buf in compress_gen(self.ctx.compressor, self.ctx.compressor_ctx, self.ctx.io, self.buffer):
                    yield self._write(buf)

                yield self._write_data_descriptor()
            finally:
                self._set_header()
                self._clear_ctx()

    async def add_file_async(self, path: Union[bytes, str], io: BufferedIOBase, utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="") -> AsyncGenerator[bytes, None]:
        """Adds file and returns async Generator object."""
        with io:
            # Create file context.
            self.ctx = self._new_file_ctx(
                path, io, utc_time, compression, comment
            )

            # Yield file's header and content.
            try:
                yield self._write_local_file()

                async for buf in compress_gen_async(self.ctx.compressor, self.ctx.compressor_ctx, self.ctx.io, self.buffer):
                    yield self._write(buf)

                yield self._write_data_descriptor()
            finally:
                self._set_header()
                self._clear_ctx()

    def add_folder(self, path: Union[bytes, str], utc_time: Optional[float] = None, comment="") -> bytes:
        """Adds folder and returns Generator object."""
        if self.ctx is not None:
            raise ValueError("File operation pending.")

        if isinstance(comment, str):
            comment = comment.encode("utf8")

        path = norm_path(path, True)
        if path in self.headers:
            raise ValueError("Path already in headers.")

        offset = self.offset
        time, date = dos_time(utc_time)

        # LocalFile
        buf = self._write(pack_header_with_data(HEADER_LOCAL_FILE, LocalFile(
            self.version_extract,
            0,  # Flag
            0,  # Compression
            time,
            date,
            0,  # Crc32
            0,  # Compressed size
            0,  # Uncompressed size
            len(path),
            0,  # Len extra
        ), path))

        # CentralDirectory
        self.headers[path] = pack_header_with_data(HEADER_CENTRAL_DIRECTORY, CentralDirectory(
            self.version_made,
            self.version_extract,
            0,  # Flag
            0,  # Compression
            time,
            date,
            0,  # Crc32
            0,  # Compressed len
            0,  # Uncompressed len
            len(path),
            0,  # Len extra
            len(comment),
            0,  # Disks tart
            0,  # Internal attr
            0,  # Externall attr
            offset,
        ), path, b"", comment,)

        return buf

    def walk(self, src: AnyStr, dist: AnyStr, utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="",
             no_compress=DEFAULT_NO_COMPRESS_FILE_EXTENSIONS) -> Generator[bytes, None, None]:
        """Generates the file headers and contents from src directory."""
        for curdir, _, files in walk(src, followlinks=False):
            # Relative path
            rpath = relpath(curdir, src)

            # Create folder
            if len(files) == 0:
                path = norm_path(join(dist, rpath), True)
                yield self.add_folder(path)

            # Write files
            for file in files:
                # Check if file extension in no_compress
                ext = splitext(file)[1].lower()
                file_compression = COMPRESSION_STORED if ext in no_compress else compression

                # Join path and open file.
                fpath = join(curdir, file)
                path = norm_path(join(dist, rpath, file), False)
                fs = open(fpath, "rb")

                # Yield file contents
                for buf in self.add_file(path, fs, utc_time, file_compression, comment):
                    yield buf

    async def walk_async(self, src: AnyStr, dist: AnyStr, utc_time: Optional[float] = None, compression=COMPRESSION_STORED, comment="",
                         no_compress=DEFAULT_NO_COMPRESS_FILE_EXTENSIONS) -> AsyncGenerator[bytes, None]:
        """Generates the file headers and contents from src directory asyncnorously."""
        for curdir, _, files in walk(src, followlinks=False):
            # Relative path
            rpath = relpath(curdir, src)

            # Create folder
            if len(files) == 0:
                path = norm_path(join(dist, rpath), True)
                yield self.add_folder(path)

            # Write files
            for file in files:
                # Check if file extension in no_compress
                ext = splitext(file)[1].lower()
                file_compression = COMPRESSION_STORED if ext in no_compress else compression

                # Join path and open file.
                fpath = join(curdir, file)
                path = norm_path(join(dist, rpath, file), False)
                fs = open(fpath, "rb")

                # Yield file contents
                async for buf in self.add_file_async(path, fs, utc_time, file_compression, comment):
                    yield buf

    def end(self, comment: Union[str, bytes] = "") -> bytes:
        """Returns EOCD which contains headers for all added files."""
        if isinstance(comment, str):
            comment = comment.encode("utf8")

        return self._write_end(comment)
