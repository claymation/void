import argparse
import os
import pathlib

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
        help="Watch src for changes, build, and optionally run a command",
        action="store_true")
    parser.add_argument("-W", "--watch-command",
        help="Command to run after building watched src")
    parser.add_argument("-b", "--browser",
        help="Browser to reload after building watched src")

    args = parser.parse_args()

    if not os.path.exists(args.src):
        parser.error("{} does not exist".format(args.src))

    try:
        os.makedirs(args.dstdir, exist_ok=True)
    except OSError:
        parser.error("failed to create dstdir {}".format(args.dstdir))

    def absolute(d):
        return pathlib.Path(d).absolute()

    src    = absolute(args.src)
    dstdir = absolute(args.dstdir)

    build(src, dstdir, rebuild=args.rebuild)

    if args.watch:
        watch(src, dstdir, args.watch_command, args.browser)

    if args.serve:
        serve(dstdir, args.port)

if __name__ == "__main__":
    main()
