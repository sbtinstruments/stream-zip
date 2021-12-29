from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

from stream_unzip import stream_unzip
from stream_zip import stream_zip


def test_with_stream_unzip():
    now = datetime.fromisoformat('2021-01-01 21:01:12')

    def files():
        yield 'file-1', now, (b'a', b'b')
        yield 'file-2', now, (b'c', b'd')

    assert [(b'file-1', None, b'ab'), (b'file-2', None, b'cd')] == [
        (name, size, b''.join(chunks))
        for name, size, chunks in stream_unzip(stream_zip(files()))
    ]


def test_with_zipfile():
    now = datetime.fromisoformat('2021-01-01 21:01:12')

    def files():
        yield 'file-1', now, (b'a', b'b')
        yield 'file-2', now, (b'c', b'd')

    with ZipFile(BytesIO(b''.join(stream_zip(files())))) as my_zip:
        pass
