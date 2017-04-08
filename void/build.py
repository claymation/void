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

environment = Environment(
    extensions=["jinja2.ext.do"],
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

    # allow local templates to override package templates
    environment.loader.loaders.insert(0,
            FileSystemLoader(os.path.join(srcroot, "_templates")))

    for src, dst in zip(os.fwalk(srcroot), os.fwalk(dstroot)):
        srcdir, srcdirs, srcfiles, srcdirfd = src
        dstdir, dstdirs, dstfiles, dstdirfd = dst

        # ignore hidden and special files and directories
        srcdirs[:] = [d for d in srcdirs if not is_hidden_or_special(d)]
        srcfiles[:] = [f for f in srcfiles if not is_hidden_or_special(f)]

        # do not descend into dstroot if it is a subdirectory of srcroot
        srcdirs[:] = [d for d in srcdirs if os.path.abspath(os.path.join(srcdir, d)) != os.path.abspath(dstroot)]

        build_dirs(srcdirs, dstdirs, dstdir)
        build_files(srcfiles, dstfiles, srcdir, dstdir, rebuild=rebuild)

def is_hidden_or_special(x):
    return x.startswith(".") or x.startswith("_")

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

    if ext in (".markdown", ".mkd", ".md"):
        fn = render_markdown
        dstfile = "".join([base, os.extsep, "html"])
    elif ext in (".html", ".htm"):
        fn = render_html
    else:
        fn = copy

    maybe(fn,
          os.path.join(srcdir, srcfile),
          os.path.join(dstdir, dstfile),
          rebuild=rebuild)
    return dstfile

def maybe(fn, src, dst, rebuild=False):
    if rebuild or missing(dst) or updated(src, dst):
        fn(src, dst)

def missing(f):
    return not os.path.exists(f)

def updated(p, q):
    return os.path.getmtime(p) > os.path.getmtime(q)

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
        "headings": extract_headings(ast),
        "content": renderer.render(ast),
    }
    template = environment.get_template("page.html")
    render_template(template, dst, context)

def render_html(src, dst):
    print("render {} {}".format(src, dst))
    with open(src, "r") as f:
        source = f.read()

    code = environment.compile(source, src, src)
    context = {}
    template = environment.template_class.from_code(environment, code, globals())
    render_template(template, dst, context)

def render_template(template, dst, context):
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

def extract_headings(ast):
    headings = []
    for node, entering in ast.walker():
        if entering and node.t == "heading":
            headings.append((node.level, node.first_child.literal))
    return headings
