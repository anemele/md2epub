import os.path as op
import re
from typing import Iterable

from .consts import ENCODING

PATTERN_TITLE = re.compile(r'^#{1,6}\s', re.M)  # NOTICE mutilline flag


def _split_chapters(text: str) -> Iterable[str]:
    its = PATTERN_TITLE.finditer(text)
    pos0 = next(its).start()
    for it in its:
        pos1 = it.start()
        yield text[pos0:pos1]
        pos0 = pos1
    yield text[pos0:]


def split_files(paths: list[str], root: str) -> Iterable[Iterable[str]]:
    for path in paths:
        path = op.join(root, path)
        with open(path, encoding=ENCODING) as fp:
            yield _split_chapters(fp.read())
