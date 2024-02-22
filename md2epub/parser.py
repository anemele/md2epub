import os.path as op
import tomllib
import uuid
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Optional

from .split import split_files as _split


@dataclass
class Manifest:
    id: str
    title: str
    language: str
    authors: list[str]

    cover: Optional[str]
    chapters: list[str]

    def __post_init__(self):
        if self.id == '':
            self.id = str(uuid.uuid4())


def _load_manifest(path: str) -> Manifest:
    with open(path, 'rb') as fp:
        sth = tomllib.load(fp)
    return Manifest(
        id=sth['id'],
        title=sth['title'],
        language=sth['language'],
        authors=sth['creators'],
        cover=sth.get('cover'),
        chapters=sth['chapters'],
    )


def parse(path: str) -> tuple[Manifest, Iterable[str]]:
    "input the manifest.toml file path"
    manifest = _load_manifest(path)
    chapters = _split(manifest.chapters, op.dirname(path))
    return manifest, chain(*chapters)
