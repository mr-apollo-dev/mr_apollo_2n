from typing import Any, Dict, Literal
from urllib.parse import urlparse

from dateutil.parser import parse  # type: ignore


class WebsiteNodeModel:
    """
    Represents an element of a website.

    Attributes
    ----------
    loc : str
            The path of the URL of the sitemap element.
    parent : str
            The path of the URL of the parent sitemap from which this element was extracted.
    element_type : Literal['url', 'sitemap']
            The type of the element.
    lastmod : datetime.datetime, optional
            The last modification date of the element.
    priority : float, optional
            The priority of the element in the sitemap.
    changefreq : str, optional
            The change frequency of the element.
    properties : dict
            The additional properties of the element.
    """

    def __init__(
        self,
        loc: str,
        parent: str,
        element_type: Literal["URL", "SITEMAP"],
        properties: Dict[str, Any],
        meta: Dict[str, Any],
    ):
        self.loc = loc
        properties.pop("loc", None)

        self.parent = parent
        self.domain = urlparse(loc).netloc
        self.element_type = element_type

        lastmod = properties.pop("lastmod", "")
        if lastmod is not None and isinstance(lastmod, str) and lastmod != "":
            try:
                self.lastmod = parse(lastmod)
            except Exception:  # noqa
                self.lastmod = None

        priority = properties.pop("priority", "")
        if (
            priority is not None
            and isinstance(priority, (str, float))
            and priority != ""
        ):
            self.priority = float(priority)

        changefreq = properties.pop("changefreq", "")
        if changefreq is not None and isinstance(changefreq, str) and changefreq != "":
            self.changefreq = changefreq

        self.properties = {k: v for k, v in properties.items() if v is not None}
        self.meta = meta

    def __repr__(self):
        return (
            "SitemapElement["
            f"\n\tloc={self.loc}, "
            f"\n\tdomain={self.domain}, "
            f"\n\tparent={self.parent}, "
            f"\n\telement_type={self.element_type}, "
            f"\n\tlastmod={self.lastmod}, "
            f"\n\tpriority={self.priority}, "
            f"\n\tchangefreq={self.changefreq}, "
            f"\n\tproperties={self.properties}, "
            f"\n\tmeta={self.meta}"
            f"]"
        )

    def to_dict(self):
        return {
            "loc": self.loc,
            "domain": self.domain,
            "parent": self.parent,
            "element_type": self.element_type,
            "lastmod": self.lastmod,
            "priority": self.priority,
            "changefreq": self.changefreq,
            "properties": self.properties,
            "meta": self.meta,
        }
