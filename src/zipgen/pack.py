from struct import pack
from typing import NamedTuple, Tuple, Union


__all__ = (
    "LocalFile",
    "ExtendedInformation64",
    "DataDescriptor",
    "DataDescriptor64",
    "CentralDirectory",
    "CentralDirectoryRecord64",
    "CentralDirectoryLocator64",
    "EndOfCentralDirectory",
    "ZipHeader",
    "pack_header",
    "pack_header_with_data",
)


class LocalFile(NamedTuple):
    version: int
    flag: int
    compression: int
    time: int
    date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    len_filename: int
    len_extra: int


class ExtendedInformation64(NamedTuple):
    size: int
    original_size: int
    compressed_size: int
    relative_header_offset: int
    disk_start_number: int


class DataDescriptor(NamedTuple):
    crc32: int
    compressed_size: int
    uncompressed_size: int


class DataDescriptor64(NamedTuple):
    crc32: int
    compressed_size: int
    uncompressed_size: int


class CentralDirectory(NamedTuple):
    version_create: int
    version_system: int
    version_extract: int
    flag: int
    compression: int
    time: int
    date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    len_filename: int
    len_extra: int
    len_comment: int
    disk_start: int
    internal_attributes: int
    external_attributes: int
    relative_offset: int


class CentralDirectoryRecord64(NamedTuple):
    size: int
    version_create: int
    version_system: int
    version_extract: int
    disk_number: int
    disk_start: int
    disk_records: int
    total_records: int
    size_cdir: int
    offset: int


class CentralDirectoryLocator64(NamedTuple):
    disk_number: int
    relative_offset: int
    total_disks: int


class EndOfCentralDirectory(NamedTuple):
    disk_number: int
    disk_start: int
    disk_records: int
    total_records: int
    size_cdir: int
    offset: int
    len_comment: int


ZipHeader = Union[
    LocalFile,
    ExtendedInformation64,
    DataDescriptor,
    DataDescriptor64,
    CentralDirectory,
    CentralDirectoryRecord64,
    CentralDirectoryLocator64,
    EndOfCentralDirectory,
]


def pack_header(struct: Tuple[bytes, int], header: ZipHeader) -> bytes:
    """Packs header returning bytes."""
    return pack(*struct, *header)


def pack_header_with_data(struct: Tuple[bytes, int], header: ZipHeader, *data: bytes) -> bytes:
    """Packs header with given data on end returning bytes."""
    return b"".join((
        pack(*struct, *header),
        *data,
    ))
