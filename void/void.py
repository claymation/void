import argparse
import os

def main():
    parser = argparse.ArgumentParser(
        description="Render HTML content from Markdown source")
    parser.add_argument("srcdir",
        help="Source directory")
    parser.add_argument("dstdir",
        help="Destination directory")

    args = parser.parse_args()

    if not (os.path.exists(args.srcdir) and os.path.isdir(args.srcdir)):
        parser.error("{} is not a directory".format(args.srcdir))

    try:
        os.makedirs(args.dstdir, exist_ok=True)
    except OSError:
        parser.error("{} is not a directory".format(args.dstdir))

if __name__ == "__main__":
    main()
