# zipgen

Zipgen is a simple and performant zip archive generator for Python 3.7 and
later. It supports ZIP64, uncompressed and various compression formats such as:
Deflated, Bzip and LZMA.

Zipgen supports synchronous asynchronous generation. Zipgen can zip archives on
the fly from stream objects such as FileIO, BytesIO and Async StreamReader.

Zipgen also supports recursive creation of zip archives from existing folders
synchronously or asynchronously.
