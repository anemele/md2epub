import os.path as op

from markdown import Markdown

from . import epublib as epub
from .parser import parse


def create_epub(path: str) -> str:
    """`path`: manifest file path"""
    manifest, chapters = parse(path)

    book = epub.EpubBook()
    book.set_uid(manifest.id)
    book.set_title(manifest.title)
    book.set_language(manifest.language)
    for author in manifest.authors:
        book.add_author(author)
    if manifest.cover is not None:
        cover_path = op.join(op.dirname(path), manifest.cover)
        with open(cover_path, 'rb') as fp:
            book.set_cover('image/cover.png', fp.read())
        book.toc.append('cover')
        book.spine.append('cover')

    markdown = Markdown()
    epub_htmls = [
        epub.EpubHtml(
            title=chapter.split('\n', 1)[0].lstrip('#').strip(),
            file_name=f'chp{i}.xhtml',
            content=markdown.convert(chapter).encode(),
        )
        for i, chapter in enumerate(chapters)
    ]
    for html in epub_htmls:
        book.add_item(html)

    book.toc.extend(epub_htmls)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine.append('nav')

    book.spine.extend(epub_htmls)

    # define css style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";

    body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
    }

    h2 {
        text-align: left;
        text-transform: uppercase;
        font-weight: 200;
    }

    ol {
        list-style-type: none;
    }

    ol > li:first-child {
        margin-top: 0.3em;
    }


    nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
    }


    nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
    }

    '''

    # add css file
    book.add_item(
        epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style.encode(),
        )
    )

    filename = f'{manifest.title}.epub'
    # epub.write_epub(filename, book)
    with epub.EpubWriter(book) as writer:
        writer.write()

    return filename
