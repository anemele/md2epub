from enum import IntEnum, auto


# LIST OF POSSIBLE ITEMS
class ItemType(IntEnum):
    UNKNOWN = auto()
    IMAGE = auto()
    STYLE = auto()
    SCRIPT = auto()
    NAVIGATION = auto()
    VECTOR = auto()
    FONT = auto()
    VIDEO = auto()
    AUDIO = auto()
    DOCUMENT = auto()
    COVER = auto()
    SMIL = auto()


# EXTENSION MAPPER
_EXTENSIONS = {
    ItemType.IMAGE: ('.jpg', '.jpeg', '.gif', '.tiff', '.tif', '.png'),
    ItemType.STYLE: ('.css'),
    ItemType.VECTOR: ('.svg'),
    ItemType.FONT: ('.otf', '.woff', '.ttf'),
    ItemType.SCRIPT: ('.js'),
    ItemType.NAVIGATION: ('.ncx'),
    ItemType.VIDEO: ('.mov', '.mp4', '.avi'),
    ItemType.AUDIO: ('.mp3', '.ogg'),
    ItemType.COVER: ('.jpg', '.jpeg', '.png'),
    ItemType.SMIL: ('.smil'),
}
EXTENSIONS: dict[str, ItemType] = {
    ext: t for t, exts in _EXTENSIONS.items() for ext in exts
}

NAMESPACES = {
    'XML': 'http://www.w3.org/XML/1998/namespace',
    'EPUB': 'http://www.idpf.org/2007/ops',
    'DAISY': 'http://www.daisy.org/z3986/2005/ncx/',
    'OPF': 'http://www.idpf.org/2007/opf',
    'CONTAINERNS': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'DC': 'http://purl.org/dc/elements/1.1/',
    'XHTML': 'http://www.w3.org/1999/xhtml',
}

CONTAINER_PATH = 'META-INF/container.xml'

CONTAINER_XML = '''<?xml version="1.0" encoding="utf-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile media-type="application/oebps-package+xml" full-path="{folder_name}/content.opf"/>
  </rootfiles>
</container>
'''

NCX_XML = b'''<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" />'''

NAV_XML = b'''<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"/>'''

CHAPTER_XML = b'''<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"  epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#"></html>'''

COVER_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
 <head>
  <style>
   body { margin: 0em; padding: 0em; }
   img { max-width: 100%; max-height: 100%; }
  </style>
 </head>
 <body>
  <img src="" alt="" />
 </body>
</html>'''
