import argparse

parser = argparse.ArgumentParser()
parser.add_argument('manifest')

args = parser.parse_args()
arg_manifest: str = args.manifest

from md2epub import create_epub

path = create_epub(arg_manifest)
print(f'save at {path}')
