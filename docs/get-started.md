---
layout: sub-navigation
order: 1
title: Get started
---


## Prerequisites

Python 3.6.7+


## Installation

You can install stream-zip from [PyPI](https://pypi.org/project/stream-zip/) using pip.

```shell
pip install stream-zip
```

This installs the latest version of stream-zip.

If you regularly install stream-zip, such as during application deployment, to avoid unexpected changes as new versions are released, you can pin to a specific version. [Poetry](https://python-poetry.org/) or [pip-tools](https://pip-tools.readthedocs.io/en/latest/) are popular tools that can be used for this.


## ZIP files

Some understanding of ZIP files is needed to use stream-zip. A ZIP file is a collection of member files, where each member file has 5 properties.

1. File name
2. Modification time
3. Mode (File type and permissions)
4. Method (Compression mechanism)
5. Binary contents

stream-unzip does not offer defaults for any of these 5 properties.


## Basic usage

A single function is exposed, `stream_zip`. This function takes an iterable of member files, and returns an iterable yielding the bytes of the ZIP file. Each member file must be a tuple of the above 5 properties.

```python
from datetime import datetime
from stat import S_IFREG
from stream_zip import ZIP_32, stream_zip

member_files = (
    (
        'my-file-1.txt',     # File name
        datetime.now(),      # Modification time
        S_IFREG | 0o600,     # Mode - regular file that owner can read and write
        ZIP_32,              # ZIP_32 has good support but limited to 4GiB
        (b'Some bytes 1',),  # Iterable of chunks of contents
    ),
    (
        'my-file-2.txt',
        datetime.now(),
        S_IFREG | 0o600,
        ZIP_32,
        (b'Some bytes 2',),
    ),
)
zipped_chunks = stream_zip(member_files):

for zipped_chunk in zipped_chunks:
    print(zipped_chunk)
```

## Generators

In the above example `member_files` is a tuple. However, any iterable that yields tuples can be used, for example a generator.

```python
from datetime import datetime
from stat import S_IFREG
from stream_zip import ZIP_32, stream_zip

def member_files():
    modified_at = datetime.now()
    mode = S_IFREG | 0o600
    yield ('my-file-1.txt', modified_at, mode, ZIP_32, (b'Some bytes 1',))
    yield ('my-file-2.txt', modified_at, mode, ZIP_32, (b'Some bytes 2',))

zipped_chunks = stream_zip(member_files()):

for zipped_chunk in zipped_chunks:
    print(zipped_chunk)
```

Each iterable of binary chunks of file contents could itself be a generator.

```python
from datetime import datetime
from stat import S_IFREG
from stream_zip import ZIP_32, stream_zip

def member_files():
    modified_at = datetime.now()
    mode = S_IFREG | 0o600

    def file_1_data():
        yield b'Some bytes 1'

    def file_2_data():
        yield b'Some bytes 2'

    yield ('my-file-1.txt', modified_at, mode, ZIP_32, file_1_data())
    yield ('my-file-2.txt', modified_at, mode, ZIP_32, file_2_data())

zipped_chunks = stream_zip(member_files()):

for zipped_chunk in zipped_chunks:
    print(zipped_chunk)
```

This pattern of generators is typical for stream-unzip. Depending on how the generators are defined, it allows avoiding loading all the bytes of member files into memory at once.


## Symbolic links

Symbolic links can be stored in ZIP files. The mode must have `stat.S_IFLNK`, and the binary contents of the file must be the path to the target of the symbolic link.

```python
from datetime import datetime
from stat import S_IFLNK
from stream_zip import ZIP_32

link = ('source.txt', datetime.now(), S_IFLNK | 0o600, ZIP_32, (b'target.txt',))
```


## Directories

Directories can be stored in ZIP files as empty member files whose name ends with a forward slash `/` that also have `stat.S_IFDIR` in the mode.

```python
from datetime import datetime
from stat import S_IFDIR
from stream_zip import ZIP_32

directory = ('my-dir/', datetime.now(), S_IFDIR | 0o700, ZIP_32, ())
```

The `stat.S_IFDIR` on the file is technically optional, but is probably good practice since it will match the resulting directory after extraction. The permissions on the directory, in the above case `0o700`, are not preserved by all clients on extraction.

It is not required to have a directory member file in order to have files in that directory. So this pattern is most useful to have empty directories in the ZIP.


## Methods

Each member file is compressed with a method that must be specified in client code. See [Methods](/methods/) for an explanation of each.


## Stream unzipping

In general, not all valid ZIP files are possible to be stream unzipped. However, all files generated by stream-zip are suitable for stream unzipping, for example by [stream-unzip](https://stream-unzip.docs.trade.gov.uk/).


## Limitations

The `NO_COMPRESSION_32` and `NO_COMPRESSION_64` methods do not stream - they buffer the entire binary contents of the file in memory before output. They do this to calculate the length and CRC 32 to output them before the binary contents in the ZIP. This is required in order for ZIP to be stream unzippable.

However, if you are able to calculate the length and CRC 32 ahead of time, you can pass `NO_COMPRESSION_32(uncompressed_size, crc_32)` or`NO_COMPRESSION_64(uncompressed_size, crc_32)` as the method. These methods do not buffer the binary contents in memory, and so are streaming methods. See [Methods](/methods/) for details of all supported methods.

Note that even for the streaming methods, it's not possible to _completely_ stream-write ZIP files. Small bits of metadata for each member file, such as its name, must be placed at the _end_ of the ZIP. In order to do this, stream-zip buffers this metadata in memory until it can be output. This is likely to only to make a meaningful difference to memory usage for extremely high numbers of member files.