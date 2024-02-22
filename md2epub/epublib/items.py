import posixpath as zip_path
from typing import Iterable, Optional

from lxml import etree

from .consts import *
from .utils import parse_html_string, parse_string

# TOC and navigation elements


class Section:
    def __init__(self, title: str, href: str):
        self.title = title
        self.href = href


class Link:
    def __init__(self, href: str, title: str, uid: str = ''):
        self.href = href
        self.title = title
        self.uid = uid


# Items


class EpubItem:
    """
    Base class for the items in a book.
    """

    def __init__(
        self,
        uid: str = '',
        file_name: str = '',
        media_type: str = '',
        content: bytes = b'',
        manifest: bool = True,
    ):
        self.uid = uid
        self.file_name = file_name
        self.media_type = media_type
        self.content = content
        self.is_linear = True  # ?
        self.manifest = manifest

    @property
    def type(self):
        """
        Guess type according to the file extension.
        Might not be the best way how to do it, but it works for now.
        """
        _, ext = zip_path.splitext(self.file_name)
        return EXTENSIONS.get(ext.lower(), ItemType.UNKNOWN)

    def __str__(self):
        # return f'<{self.__class__.__name__}:{self.uid}>'
        return f'<{self.__class__.__name__}:{self.uid}:{self.file_name}>'


class EpubNcx(EpubItem):
    "Navigation Control File (NCX)"

    def __init__(self, uid='ncx', file_name='toc.ncx'):
        super().__init__(
            uid=uid, file_name=file_name, media_type='application/x-dtbncx+xml'
        )


class EpubCover(EpubItem):
    def __init__(self, uid='cover-img', file_name=''):
        super().__init__(uid=uid, file_name=file_name)

    @property
    def type(self):
        return ItemType.COVER


class EpubHtml(EpubItem):
    def __init__(
        self,
        uid: str = '',
        file_name: str = '',
        media_type: str = '',
        content: bytes = b'',
        title: str = '',
        language: str = '',
        direction=None,
        media_overlay=None,
        media_duration=None,
    ):
        super().__init__(uid, file_name, media_type, content)

        self.title = title
        self.language = language
        self.direction = direction

        self.media_overlay = media_overlay
        self.media_duration = media_duration

        self.links = []
        self.properties = []
        self.pages = []

        self.is_chapter = True

    @property
    def type(self):
        return ItemType.DOCUMENT

    def add_link(self, **kw):
        """
        Add additional link to the document. Links will be embeded only inside of this document.

        >>> add_link(href='styles.css', rel='stylesheet', type='text/css')
        """
        self.links.append(kw)
        if kw.get('type') == 'text/javascript':
            if 'scripted' not in self.properties:
                self.properties.append('scripted')

    def get_links(self):
        """
        Returns list of additional links defined for this document.

        :Returns:
          As tuple return list of links.
        """
        return (link for link in self.links)

    def get_links_of_type(self, link_type: str):
        """
        Returns list of additional links of specific type.

        :Returns:
          As tuple returns list of links.
        """
        return (link for link in self.links if link.get('type') == link_type)

    def add_item(self, item: EpubItem):
        """
        Add other item to this document. It will create additional links according to the item type.

        :Args:
          - item: item we want to add defined as instance of EpubItem
        """
        if item.type == ItemType.STYLE:
            self.add_link(href=item.file_name, rel='stylesheet', type='text/css')
        elif item.type == ItemType.SCRIPT:
            self.add_link(src=item.file_name, type='text/javascript')

    def get_body_content(self) -> bytes:
        """
        Returns content of BODY element for this HTML document. Content will be of type 'str' (Python 2)
        or 'bytes' (Python 3).

        :Returns:
          Returns content of this document.
        """

        try:
            html_tree = parse_html_string(self.content)
        except:
            return b''

        html_root = html_tree.getroottree()

        tmp = html_root.find('body')
        if tmp is None:
            return b''

        if len(tmp) == 0:
            return b''

        body = html_tree.find('body')
        if body is None:
            return b''

        tree_str = etree.tostring(
            body, pretty_print=True, encoding='utf-8', xml_declaration=False
        )

        return tree_str.lstrip(b'<body>').rstrip(b'</body>')

    def get_content(self) -> bytes:
        """
        Returns content for this document as HTML string. Content will be of type 'str' (Python 2)
        or 'bytes' (Python 3).

        :Args:
          - default: Default value for the content if it is not defined.

        :Returns:
          Returns content of this document.
        """

        tree = parse_string(CHAPTER_XML)
        tree_root = tree.getroot()

        tree_root.set('lang', self.language)
        tree_root.attrib['{%s}lang' % NAMESPACES['XML']] = self.language

        # add to the head also
        #  <meta charset="utf-8" />

        try:
            html_tree = parse_html_string(self.content)
        except:
            return b''

        # html_root = html_tree.getroottree()

        # create and populate head

        _head = etree.SubElement(tree_root, 'head')

        if self.title != '':
            _title = etree.SubElement(_head, 'title')
            _title.text = self.title

        for lnk in self.links:
            if lnk.get('type') == 'text/javascript':
                _lnk = etree.SubElement(_head, 'script', lnk)
                # force <script></script>
                _lnk.text = ''
            else:
                _lnk = etree.SubElement(_head, 'link', lnk)

        # this should not be like this
        # head = html_root.find('head')
        # if head is not None:
        #     for i in head.getchildren():
        #         if i.tag == 'title' and self.title != '':
        #             continue
        #         _head.append(i)

        # create and populate body

        _body = etree.SubElement(tree_root, 'body')
        if self.direction:
            _body.set('dir', self.direction)
            tree_root.set('dir', self.direction)

        body = html_tree.find('body')
        if body is not None:
            for i in body.iterchildren():
                _body.append(i)

        tree_str = etree.tostring(
            tree, pretty_print=True, encoding='utf-8', xml_declaration=True
        )

        return tree_str


class EpubCoverHtml(EpubHtml):

    """
    Represents Cover page in the EPUB file.
    """

    def __init__(
        self, uid='cover', file_name='cover.xhtml', image_name='', title='Cover'
    ):
        super().__init__(uid=uid, file_name=file_name, title=title)

        self.image_name = image_name
        self.is_linear = False
        self.is_chapter = False

    def get_content(self):
        """
        Returns content for cover page as HTML string. Content will be of type 'str' (Python 2) or 'bytes' (Python 3).

        :Returns:
          Returns content of this document.
        """

        self.content = COVER_XML

        tree = parse_string(super().get_content())
        tree_root = tree.getroot()

        images = tree_root.xpath(
            '//xhtml:img', namespaces={'xhtml': NAMESPACES['XHTML']}
        )

        images[0].set('src', self.image_name)
        images[0].set('alt', self.title)

        tree_str = etree.tostring(
            tree, pretty_print=True, encoding='utf-8', xml_declaration=True
        )

        return tree_str


class EpubNav(EpubHtml):

    """
    Represents Navigation Document in the EPUB file.
    """

    def __init__(
        self,
        uid='nav',
        file_name='nav.xhtml',
        media_type='application/xhtml+xml',
        title='',
        direction=None,
    ):
        super().__init__(
            uid=uid,
            file_name=file_name,
            media_type=media_type,
            title=title,
            direction=direction,
        )

        self.is_chapter = False


class EpubImage(EpubItem):

    """
    Represents Image in the EPUB file.
    """

    @property
    def type(self):
        return ItemType.IMAGE


class EpubSMIL(EpubItem):
    def __init__(self, uid='', file_name='', content=b''):
        super().__init__(
            uid=uid,
            file_name=file_name,
            media_type='application/smil+xml',
            content=content,
        )

    @property
    def type(self):
        return ItemType.SMIL


def get_headers(elem):
    for n in range(1, 7):
        headers = elem.xpath(f'./h{n}')
        if len(headers) == 0:
            continue

        text = headers[0].text_content().strip()
        if len(text) > 0:
            return text


def get_pages(item: EpubHtml) -> Iterable[tuple[str, str, str]]:
    body = parse_html_string(item.get_body_content())

    for elem in body.iter():
        if 'epub:type' not in elem.attrib:
            continue

        id = elem.get('id')
        if id is None:
            continue

        text = None

        if elem.text is not None and elem.text.strip() != '':
            text = elem.text.strip()

        if text is None:
            text = elem.get('aria-label')

        if text is None:
            text = get_headers(elem)

        yield (item.file_name, id, text or id)


def get_pages_for_items(items: Iterable[EpubHtml]) -> list[str]:
    return [page for item in items for pages in get_pages(item) for page in pages]
