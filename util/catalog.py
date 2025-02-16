import os
from urllib.parse import quote
from uuid import uuid4

from flask import url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .entry import Entry
from .link import Link


class Catalog(object):
    def __init__(
            self,
            title,
            id=None,
            description=None,
            author_name=None,
            author_uri=None,
            root_url=None,
            url=None,
            entries=None,
    ):
        self.title = title
        self.description = description
        self.id = id or uuid4()
        self.author_name = author_name
        self.author_uri = author_uri
        self.root_url = root_url
        self.url = url
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)

    def render(self, view_mode=None, catalog_entries=None, loading=False):
        env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(os.path.dirname(__file__), "../templates")
            ),
            autoescape=select_autoescape(["html", "xml"]),
        )
        env.globals['url_for'] = url_for

        # if loading:
        #     template = env.get_template("loading.opds.jinja2")
        #     return template.render(loading=loading)
        # else:
        template = env.get_template("catalog.opds.jinja2")
        return template.render(catalog=self, view_mode=view_mode, catalog_entries=catalog_entries)


def fromdir(root_url, url, content_base_path, content_relative_path):
    path = os.path.join(content_base_path, content_relative_path)
    print(path)
    c = Catalog(
        title=os.path.basename(os.path.dirname(path)), root_url=root_url, url=url
    )
    onlydirs = [
        f for f in os.listdir(path) if not os.path.isfile(os.path.join(path, f))
    ]
    print(onlydirs)
    for dirname in onlydirs:
        link = Link(
            href=quote(f"/catalog/{content_relative_path}/{dirname}"),
            rel="subsection",
            type="application/atom+xml;profile=opds-catalog;kind=acquisition",
        )
        c.add_entry(Entry(title=dirname, id=uuid4(), links=[link], is_folder=True))  # Mark as folder

    onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    print(onlyfiles)
    for filename in onlyfiles:
        link = Link(
            href=quote(f"/content/{content_relative_path}/{filename}"),
            rel="http://opds-spec.org/acquisition",
            type=mimetype(filename),
        )
        c.add_entry(Entry(title=filename.split(".")[0], id=uuid4(), links=[link], is_folder=False))  # Mark as file
    return c


def mimetype(path):
    extension = path.split(".")[-1].lower()
    if extension == "pdf":
        return "application/pdf"
    elif extension == "epub":
        return "application/epub"
    elif extension == "mobi":
        return "application/mobi"
    elif extension == "fb2":
        return "application/fb2"
    else:
        return "application/unknown"
