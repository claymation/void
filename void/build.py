import contextlib
import os
import shutil
import subprocess
import tempfile

import CommonMark

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader


@contextlib.contextmanager
def cd(newdir):
    olddir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(olddir)

env = Environment(
    loader=ChoiceLoader([
        PackageLoader("void"),
    ]), autoescape=True)

def build(srcroot, dstroot, rebuild=False):
    """
    Copy the contents of srcroot to dstroot, recursively,
    rendering Markdown files to HTML along the way.
    """
    # if a source file is given, render it and return
    if os.path.isfile(srcroot):
        build_files([srcroot], [], os.path.dirname(srcroot), dstroot)
        return

    for src, dst in zip(os.fwalk(srcroot), os.fwalk(dstroot)):
        srcdir, srcdirs, srcfiles, srcdirfd = src
        dstdir, dstdirs, dstfiles, dstdirfd = dst

        # ignore hidden files and directories
        srcdirs[:] = [d for d in srcdirs if not d.startswith(".")]
        srcfiles[:] = [f for f in srcfiles if not f.startswith(".")]

        # do not descend into dstroot if it is a subdirectory of srcroot
        srcdirs[:] = [d for d in srcdirs if os.path.abspath(os.path.join(srcdir, d)) != os.path.abspath(dstroot)]

        build_dirs(srcdirs, dstdirs, dstdir)
        build_files(srcfiles, dstfiles, srcdir, dstdir, rebuild=rebuild)

def build_dirs(srcdirs, dstdirs, dstdir):
    srcdirset = set(srcdirs)
    dstdirset = set(dstdirs)

    # remove directories in dstdirs not in srcdirs
    for d in (dstdirset - srcdirset):
        print("rmtree {}".format(os.path.join(dstdir, d)))
        shutil.rmtree(os.path.join(dstdir, d))
        dstdirset.remove(d)

    # create directories in srcdirs not in dstdirs
    for d in (srcdirset - dstdirset):
        print("mkdir {}".format(os.path.join(dstdir, d)))
        os.mkdir(os.path.join(dstdir, d))
        dstdirset.add(d)

    # dstdirs must now equal srcdirs; make it so
    dstdirs[:] = srcdirs

def build_files(srcfiles, dstfiles, srcdir, dstdir, rebuild=False):
    dstfileset = set(dstfiles)

    for f in srcfiles:
        f = copy_or_render(f, srcdir, dstdir, rebuild=rebuild)
        dstfileset.discard(f)

    # remove files in dstdir not in srcdir
    for f in dstfileset:
        print("rm {}".format(os.path.join(dstdir, f)))
        os.unlink(os.path.join(dstdir, f))

def copy_or_render(srcfile, srcdir, dstdir, rebuild=False):
    dstfile = srcfile
    base, ext = os.path.splitext(srcfile)

    if ext in (".markdown", ".md"):
        dstfile = "".join([base, os.extsep, "html"])
        maybe(render_markdown,
              os.path.join(srcdir, srcfile),
              os.path.join(dstdir, dstfile),
              rebuild=rebuild)
    else:
        maybe(copy,
              os.path.join(srcdir, srcfile),
              os.path.join(dstdir, dstfile),
              rebuild=rebuild)
    return dstfile

def maybe(fn, src, dst, rebuild=False):
    if rebuild or not os.path.exists(dst) or mtime(src) > mtime(dst):
        fn(src, dst)

def mtime(f):
    return os.stat(f).st_mtime

def copy(src, dst):
    print("cp {} {}".format(src, dst))
    shutil.copyfile(src, dst)

def render_markdown(src, dst):
    print("render {} {}".format(src, dst))
    parser = CommonMark.Parser()
    renderer = CommonMark.HtmlRenderer()
    with open(src, "r") as f:
        ast = parser.parse(f.read())
    ast = compile_code_fragments(ast)
    context = {
        "title": extract_title(ast),
        "content": renderer.render(ast),
    }
    render_template("page.html", dst, **context)

def render_template(src, dst, **context):
    template = env.get_template(src)
    html = template.render(context)

    with open(dst, "w") as f:
        f.write(html)

def compile_code_fragments(ast):
    with tempfile.TemporaryDirectory() as tmpdir:
        # extract code blocks by filename
        for node, entering in ast.walker():
            if node.t == "code_block" and node.info:
                try:
                    filetype, filename = node.info.split(maxsplit=1)
                except ValueError:
                    continue
                if not filename.startswith("!"):
                    print("  - extract {}".format(filename))
                    with open(os.path.join(tmpdir, filename), "w") as f:
                        f.write(node.literal)

        # compile code fragments
        for node, entering in ast.walker():
            if node.t == "code_block" and node.info:
                try:
                    filetype, command = node.info.split(maxsplit=1)
                except ValueError:
                    continue
                if command.startswith("!"):
                    command = command[1:]
                    print("  - exec {}".format(command))
                    with cd(tmpdir):
                        result = subprocess.run(command,
                                                shell=True,
                                                encoding="utf8",
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                        node.literal = result.stdout

    return ast

def extract_title(ast):
    for node, entering in ast.walker():
        if node.t == "heading" and node.level == 1:
            return node.first_child.literal
