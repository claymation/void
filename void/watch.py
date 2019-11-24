import subprocess

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from .build import build


class WatchHandler(PatternMatchingEventHandler):
    def __init__(self, src, dstdir, command=""):
        super(WatchHandler, self).__init__(ignore_patterns=[
            "{}/{}/*".format(src, dstdir),
            "{}/.git/*".format(src),
            "*.swp",
        ], ignore_directories=True)
        self.src = src
        self.dstdir = dstdir
        self.command = command

    def on_created(self, event):
        print("Change detected; rebuilding...")

        build(self.src, self.dstdir)

        if self.command:
            subprocess.run(self.command, shell=True)


def watch(src, dstdir, command=""):
    handler = WatchHandler(src, dstdir, command)
    observer = Observer()
    observer.schedule(handler, src, recursive=True)
    observer.start()
