import argparse
import os

from .build import build
from .serve import serve

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
    parser.add_argument("-s", "--serve",
        help="Start an HTTP server on localhost",
        action="store_true")
    parser.add_argument("-p", "--port",
        help="HTTP port",
        type=int, default=8000)

    args = parser.parse_args()

    if not os.path.exists(args.src):
        parser.error("{} does not exist".format(args.src))

    try:
        os.makedirs(args.dstdir, exist_ok=True)
    except OSError:
        parser.error("failed to create dstdir {}".format(args.dstdir))

    build(args.src, args.dstdir, rebuild=args.rebuild)

    if args.serve:
        serve(args.dstdir, args.port)

if __name__ == "__main__":
    main()
