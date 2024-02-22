from collections import OrderedDict
from typing import Optional

from .consts import *
from .items import *
from .utils import guess_type


class EpubBook:
    def __init__(self):
        self.EPUB_VERSION = None

        "Initialises all needed variables to default values"

        self.metadata = {}
        self.items: list[EpubItem] = []
        self.spine: list[EpubHtml | str] = []
        self.guide = []
        self.pages = []
        self.toc = []
        self.bindings = []

        self.IDENTIFIER_ID = 'id'
        self.FOLDER_NAME = 'EPUB'

        self._id_html = 0
        self._id_image = 0
        self._id_static = 0

        self.title = ''
        self.language = ''
        self.direction = None

        self.add_metadata(
            'OPF',
            'generator',
            '',
            {
                'name': 'generator',
                'content': __package__,
            },
        )

        # custom prefixes and namespaces to be set to the content.opf doc
        self.prefixes = []
        self.namespaces = {}

    def set_uid(self, uid: str):
        self.uid = uid

        self.set_unique_metadata(
            'DC', 'identifier', self.uid, {'id': self.IDENTIFIER_ID}
        )

    def set_title(self, title: str):
        "Set title. You can set multiple titles."

        self.title = title

        self.add_metadata('DC', 'title', self.title)

    def set_language(self, lang):
        """
        Set language for this epub. You can set multiple languages. Specific items in the book can have
        different language settings.

        :Args:
          - lang: Language code
        """

        self.language = lang

        self.add_metadata('DC', 'language', lang)

    def set_direction(self, direction):
        """
        :Args:
          - direction: Options are "ltr", "rtl" and "default"
        """

        self.direction = direction

    def set_cover(self, file_name: str, content: bytes, create_page=True):
        """
        Set cover and create cover document if needed.

        :Args:
          - file_name: file name of the cover page
          - content: Content for the cover image
          - create_page: Should cover page be defined. Defined as bool value (optional). Default value is True.
        """

        # as it is now, it can only be called once
        c = EpubCover(file_name=file_name)
        c.content = content
        self.add_item(c)

        if create_page:
            self.add_item(EpubCoverHtml(image_name=file_name))

        self.add_metadata(
            None, 'meta', '', OrderedDict(name='cover', content='cover-img')
        )

    def add_author(self, author: str, file_as=None, role=None, uid='creator'):
        "Add author for this document"

        self.add_metadata('DC', 'creator', author, {'id': uid})

        if file_as:
            self.add_metadata(
                None,
                'meta',
                file_as,
                {'refines': '#' + uid, 'property': 'file-as', 'scheme': 'marc:relators'},
            )
        if role:
            self.add_metadata(
                None,
                'meta',
                role,
                {'refines': '#' + uid, 'property': 'role', 'scheme': 'marc:relators'},
            )

    def add_metadata(
        self, namespace: Optional[str], name: str, value, others: Optional[dict] = None
    ):
        if namespace in NAMESPACES:
            namespace = NAMESPACES[namespace]

        if namespace not in self.metadata:
            self.metadata[namespace] = {}

        if name not in self.metadata[namespace]:
            self.metadata[namespace][name] = []

        self.metadata[namespace][name].append((value, others))

    def get_metadata(self, namespace: Optional[str], name: str):
        if namespace in NAMESPACES:
            namespace = NAMESPACES[namespace]

        return self.metadata[namespace].get(name, [])

    def set_unique_metadata(self, namespace, name, value, others=None):
        "Add metadata if metadata with this identifier does not already exist, otherwise update existing metadata."

        if namespace in NAMESPACES:
            namespace = NAMESPACES[namespace]

        if namespace in self.metadata and name in self.metadata[namespace]:
            self.metadata[namespace][name] = [(value, others)]
        else:
            self.add_metadata(namespace, name, value, others)

    def add_item(self, item: EpubItem):
        """
        Add additional item to the book. If not defined, media type and chapter id will be defined
        for the item.

        :Args:
          - item: Item instance
        """
        if item.media_type == '':
            has_guessed, media_type = guess_type(item.file_name.lower())

            if has_guessed is not None:
                if media_type is not None:
                    item.media_type = media_type
                else:
                    item.media_type = has_guessed
            else:
                item.media_type = 'application/octet-stream'

        if item.uid == '':
            # make chapter_, image_ and static_ configurable
            if isinstance(item, EpubHtml):
                item.uid = f'chapter_{self._id_html}'
                self._id_html += 1
                # If there's a page list, append it to the book's page list
                self.pages += item.pages
            elif isinstance(item, EpubImage):
                item.uid = f'image_{self._id_image}'
                self._id_image += 1
            else:
                item.uid = f'static_{self._id_static}'
                self._id_static += 1

        self.items.append(item)

    def get_item_with_id(self, uid: str) -> Optional[EpubItem]:
        """
        Returns item for defined UID.

        >>> book.get_item_with_id('image_001')

        :Args:
          - uid: UID for the item

        :Returns:
          Returns item object. Returns None if nothing was found.
        """
        for item in self.items:
            if item.uid == uid:
                return item

    def get_item_with_href(self, href: str) -> Optional[EpubItem]:
        """
        Returns item for defined HREF.

        >>> book.get_item_with_href('EPUB/document.xhtml')

        :Args:
          - href: HREF for the item we are searching for

        :Returns:
          Returns item object. Returns None if nothing was found.
        """
        for item in self.items:
            if item.file_name == href:
                return item

    def get_items_of_type(self, item_type: ItemType):
        """
        Returns all items of specified type.

        >>> book.get_items_of_type(epub.ITEM_IMAGE)

        :Args:
          - item_type: Type for items we are searching for

        :Returns:
          Returns found items as tuple.
        """
        return (item for item in self.items if item.type == item_type)

    def get_items_of_media_type(self, media_type: str):
        """
        Returns all items of specified media type.

        :Args:
          - media_type: Media type for items we are searching for

        :Returns:
          Returns found items as tuple.
        """
        return (item for item in self.items if item.media_type == media_type)

    def add_prefix(self, name: str, uri: str):
        """
        Appends custom prefix to be added to the content.opf document

        >>> epub_book.add_prefix('bkterms', 'http://booktype.org/')

        :Args:
          - name: namespave name
          - uri: URI for the namespace
        """

        self.prefixes.append(f'{name}: {uri}')
