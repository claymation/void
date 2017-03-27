import argparse
import os

from .build import build

def main():
    parser = argparse.ArgumentParser(
        description="Render HTML content from Markdown source")
    parser.add_argument("src",
        help="Source file or directory")
    parser.add_argument("dstdir",
        help="Destination directory")
    parser.add_argument("-r", "--rebuild",
        help="Rebuild all files, regardless of mtime",
        action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.src):
        parser.error("{} does not exist".format(args.src))

    try:
        os.makedirs(args.dstdir, exist_ok=True)
    except OSError:
        parser.error("failed to create dstdir {}".format(args.dstdir))

    build(args.src, args.dstdir, rebuild=args.rebuild)

if __name__ == "__main__":
    main()
