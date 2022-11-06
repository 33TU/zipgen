# Zip header structs and signatures.
HEADER_LOCAL_FILE = (b"<I5H3I2H", 0x04034b50,)
HEADER_DATA_DESCRIPTOR = (b"<4I", 0x08074b50,)
HEADER_DATA_DESCRIPTOR64 = (b"<2I2Q", 0x08074b50,)
HEADER_CENTRAL_DIRECTORY = (b"<I2B5H3I5H2I", 0x02014b50,)
HEADER_CENTRAL_DIRECTORY_RECORD64 = (b"<IQ2BH2I4Q", 0x06064b50,)
HEADER_CENTRAL_DIRECTORY_LOCATOR64 = (b"<2IQI", 0x07064b50,)
HEADER_END_OF_CENTRAL_DIRECTORY = (b"<I4H2IH",  0x06054b50,)

# Tag
TAG_EXTENDED_INFORMATION64 = (b"<2H3QI", 0x0001,)

# Compression methods.
COMPRESSION_STORED = 0
COMPRESSION_DEFLATED = 8
COMPRESSION_BZIP2 = 12
COMPRESSION_LZMA = 14

# Extract versions.
CREATE_DEFAULT = 20
CREATE_ZIP64 = 45
CREATE_BZIP2 = 46
CREATE_LZMA = 63

# Flags.
FLAG_EOS = 0b10
FLAG_CRC32 = 0b1000
FLAG_UTF8 = 0b100000000000
FLAG_DEFAULT_FILE = FLAG_CRC32 | FLAG_UTF8
FLAG_DEFAULT_LZMA_FILE = FLAG_DEFAULT_FILE | FLAG_EOS

# Made by versions.
MADE_BY_WINDOWS = 0
MADE_BY_UNIX = 3

# External attr
DEFAULT_EXTERNAL_ATTR = 25165824  # ?rw-------
DEFAULT_EXTERNAL_DIR_ATTR = 1107099664  # drwxrwxr-x + MS DOS directory

# 32-bit signed max.
INT32_MAX = 2147483647

# Size = SizeOfFixedFields + SizeOfVariableData - 12.
# Size is sizeof(struct HEADER_CENTRAL_DIRECTORY_RECORD64) -  12 = 44
SIZE_CENTRAL_DIRECTORY_RECORD64_REMAINING = 44

# Size = used fields's sizes combined
# Size = sizeof(struct ExtendedInformation64 - 4) = 28
SIZE_EXTENDED_INFORMATION = 28

# No compression types
DEFAULT_NO_COMPRESS_FILE_EXTENSIONS = (
    ".rar", ".7z", ".zip", ".bz", ".gz", ".tar.gz", ".tar.gz2", ".tar.lzma", "tar.bz",
    ".jpg", ".jpeg", ".jfif", ".pjpeg", ".pjp", ".png", ".apng", ".webp", ".avif", ".gif",
    ".mp3", ".aac", ".ogg", ".wma", ".flac", ".alac", ".wma",
    ".mp4", ".webm", ".mpeg",
)
