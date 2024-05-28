import argparse
from typing import Optional

from .core import create_epub
from .parser import gen_m


def main():
    parser = argparse.ArgumentParser(prog=__package__)
    parser.add_argument('-m', '--manifest')
    parser.add_argument('-g', '--generate-manifest', action='store_true')

    args = parser.parse_args()
    arg_manifest: Optional[str] = args.manifest
    arg_gen_m: bool = args.generate_manifest

    if arg_manifest is not None:
        print(create_epub(arg_manifest))
    elif arg_gen_m:
        gen_m()
    else:
        parser.print_help()
