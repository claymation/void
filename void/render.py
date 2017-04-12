from CommonMark import HtmlRenderer as CommonMarkHtmlRenderer

from slugify import slugify


class HtmlRenderer(CommonMarkHtmlRenderer):
    """
    Extends the CommonMark HTMLRenderer, adding:

      * heading ids
      * code.nohighlight if no info string is given
    """

    def heading(self, node, entering):
        tagname = "h" + str(node.level)
        attrs = self.attrs(node)
        attrs.append(["id", slugify(node.first_child.literal)])
        if entering:
            self.cr()
            self.tag(tagname, attrs)
        else:
            self.tag("/" + tagname)
            self.cr()

    def code_block(self, node, entering):
        info_words = node.info.split() if node.info else []
        attrs = self.attrs(node)
        if len(info_words) > 0 and len(info_words[0]) > 0:
            attrs.append(["class", "language-" +
                          self.escape(info_words[0], True)])
        else:
            attrs.append(["class", "nohighlight"])

        self.cr()
        self.tag("pre")
        self.tag("code", attrs)
        self.out(node.literal)
        self.tag("/code")
        self.tag("/pre")
        self.cr()
