# void
Render HTML content from Markdown source

void is a simple static web site generator designed for programmers. It's
so-named because it's devoid of the blogging features touted by other static
site generators. void has no concept of posts, authors, dates, categories,
tags, etc. void simply walks a tree of Markdown source files, passing them
through [CommonMark][] and [Jinja2][] to produce a tree of HTML output files.
You can organize and index your content as you see fit; void preserves your
directory structure and filenames.

## Programmer-friendly features:

  * Minimalist design with clean typography, courtesy of [Milligram][] styles
  * Syntax highlighting, courtesy of [highlight.js]
  * Fenced code block extraction and substitution

That last point deserves an explanation. Say you're writing about programming.
To include a code sample in your Markdown you can use a fenced code block:

    ``` python
	def hello():
	    print("Hello, void.")

	hello()
	```

	When run as `python hello.py`, we see:

	``` txt
	Hello, void.
	```

You'd like to know that your code sample doesn't contain any egregious syntax
errors, and that it produces the output that you expect. You may also want to
allow readers to download your embedded code snippets.

With void, you can give a fenced code block a filename and it'll be extracted
to a file in the output directory when rebuilding the page. Provide the
filename as the second word in the [info string][] (the first word, here
`python`, defines the language for the syntax highlighter):

	``` python hello.py
	def hello():
		print("Hello, void.")

	hello()
	```

When rendering this page the file hello.py will be created in the output
directory (adjacent to the rendered .html file). That's fenced code block
extraction.

To test your code snippet and embed its output in your rendered HTML, define
an empty fenced code block and specify a shell command prefixed with a bang
(!) in the info string:

	``` txt !python hello.py
	```

When rendering this page the given shell command will be run and its output
(stdout) will be substitued into the code block. That's fenced code block
substitution. Specifying the langugage as `txt` here is a convenient hack to
avoid syntax highlighting in the output.

## Status

void has nearly reached the minimum viable product stage. I use it to generate
my own [static web site](http://daemons.net). The few remaining things I want
to do:

  * provide more context to Jinja templates
  * maybe define a separate index.html template

## Contributing

Feel free to send me a [pull request][].


[CommonMark]: http://commonmark.org/
[Jinja2]: http://jinja.pocoo.org/
[Milligram]: https://milligram.github.io/
[highlight.js]: https://highlightjs.org/
[info string]: http://spec.commonmark.org/0.27/#info-string
[pull request]: https://github.com/claymation/void/pull/new/master
