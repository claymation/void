from CommonMark import HtmlRenderer as CommonMarkHtmlRenderer

from slugify import slugify


class HtmlRenderer(CommonMarkHtmlRenderer):
    """
    Extends the CommonMark HTMLRenderer, adding:

      * heading ids
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
