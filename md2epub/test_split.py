from .split import _split_chapters


def test_sc():
    sample = '''\
# a
abc
## b
BCD
'''
    expect = ['', '# a\nabc\n', '## b\nBCD\n']
    result = _split_chapters(sample)
    assert list(result) == expect
