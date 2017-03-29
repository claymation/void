import os
import shutil

import CommonMark

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader

env = Environment(
    loader=ChoiceLoader([
        PackageLoader("void"),
    ]), autoescape=True)

def build(srcroot, dstroot):
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
        build_files(srcfiles, dstfiles, srcdir, dstdir)

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

def build_files(srcfiles, dstfiles, srcdir, dstdir):
    dstfileset = set(dstfiles)

    for f in srcfiles:
        f = copy_or_render(f, srcdir, dstdir)
        dstfileset.discard(f)

    # remove files in dstdir not in srcdir
    for f in dstfileset:
        print("rm {}".format(os.path.join(dstdir, f)))
        os.unlink(os.path.join(dstdir, f))

def copy_or_render(srcfile, srcdir, dstdir):
    dstfile = srcfile
    base, ext = os.path.splitext(srcfile)

    if ext in (".markdown", ".md"):
        dstfile = "".join([base, os.extsep, "html"])
        maybe(render_markdown,
              os.path.join(srcdir, srcfile),
              os.path.join(dstdir, dstfile))
    else:
        maybe(copy,
              os.path.join(srcdir, srcfile),
              os.path.join(dstdir, dstfile))
    return dstfile

def maybe(fn, src, dst, force=False):
    if force or not os.path.exists(dst) or mtime(src) > mtime(dst):
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

def extract_title(ast):
    for node, entering in ast.walker():
        if node.t == "heading" and node.level == 1:
            return node.first_child.literal
