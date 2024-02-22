import mimetypes
from io import BytesIO

from lxml import etree


def parse_string(s: bytes):
    parser = etree.XMLParser(recover=True, resolve_entities=False)
    return etree.parse(BytesIO(s), parser=parser)


def parse_html_string(s: bytes):
    from lxml import html

    utf8_parser = html.HTMLParser(encoding='utf-8')

    return html.document_fromstring(s, parser=utf8_parser)


mimetype_initialised = False


def guess_type(extenstion: str):
    global mimetype_initialised

    if not mimetype_initialised:
        mimetypes.init()
        mimetypes.add_type('application/xhtml+xml', '.xhtml')
        mimetype_initialised = True

    return mimetypes.guess_type(extenstion)


def create_pagebreak(pageref, label=None, html=True):
    from .consts import NAMESPACES

    pageref_attributes = {
        '{%s}type' % NAMESPACES['EPUB']: 'pagebreak',
        'title': u'{}'.format(pageref),
        'id': u'{}'.format(pageref),
    }

    pageref_elem = etree.Element(
        'span', pageref_attributes, nsmap={'epub': NAMESPACES['EPUB']}
    )

    if label:
        pageref_elem.text = label

    if html:
        return etree.tostring(pageref_elem, encoding='unicode')  # type: ignore

    return pageref_elem
