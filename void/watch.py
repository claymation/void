import pathlib
import platform
import subprocess

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from .build import build


def reload_command(browser):
    if not browser:
        return

    srcdir = pathlib.Path(__file__).parent.absolute()
    scriptsdir = srcdir / "scripts"

    if platform.system() == "Darwin":
        script = scriptsdir / "reload.applescript"
        return f"osascript {script} {browser}"


class WatchHandler(PatternMatchingEventHandler):
    def __init__(self, src, dstdir, command="", browser=""):
        super(WatchHandler, self).__init__(ignore_patterns=[
            "{}/{}/*".format(src, dstdir),
            "{}/.git/*".format(src),
            "*.swp",
        ], ignore_directories=True)
        self.src = src
        self.dstdir = dstdir
        self.command = command
        self.reload_command = reload_command(browser)

    def on_created(self, event):
        print("Change detected; rebuilding...")

        build(self.src, self.dstdir)

        if self.command:
            subprocess.run(self.command, shell=True)

        if self.reload_command:
            subprocess.run(self.reload_command.split())


def watch(src, dstdir, command="", browser=""):
    handler = WatchHandler(src, dstdir, command, browser)
    observer = Observer()
    observer.schedule(handler, src, recursive=True)
    observer.start()
