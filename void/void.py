import argparse
import os

from .build import build
from .serve import serve
from .watch import watch


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
    parser.add_argument("-w", "--watch",
        help="Watch src for changes, rebuild, and optionally run a command",
        action="store_true")
    parser.add_argument("-W", "--watch-command",
        help="Command to run after rebuilding watched src")

    args = parser.parse_args()

    if not os.path.exists(args.src):
        parser.error("{} does not exist".format(args.src))

    try:
        os.makedirs(args.dstdir, exist_ok=True)
    except OSError:
        parser.error("failed to create dstdir {}".format(args.dstdir))

    build(args.src, args.dstdir, rebuild=args.rebuild)

    if args.watch:
        watch(args.src, args.dstdir, args.watch_command)

    if args.serve:
        serve(args.dstdir, args.port)

if __name__ == "__main__":
    main()
