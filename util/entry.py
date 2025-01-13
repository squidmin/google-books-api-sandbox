class Entry(object):
    valid_keys = (
        "id",
        "url",
        "filename",
        "title",
        "content",
        "downloadsPerMonth",
        "updated",
        "identifier",
        "date",
        "rights",
        "summary",
        "dcterms_source",
        "provider",
        "publishers",
        "contributors",
        "languages",
        "subjects",
        "oai_updatedates",
        "authors",
        "formats",
        "links",
        "thumbnail",
        "small_thumbnail",
        "isbn",
        "is_folder",
        "canonical_volume_link",
        "description",
    )

    required_keys = ("id", "title", "links")

    def validate(self, key, value):
        if key not in Entry.valid_keys:
            raise KeyError("invalid key in opds.catalog.Entry: %s" % (key))

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            self.validate(key, val)

        for req_key in Entry.required_keys:
            if not req_key in kwargs:
                raise KeyError("required key %s not supplied for Entry!" % (req_key))

        self.id = kwargs["id"]
        self.filename = kwargs.get("filename", None)
        self.title = kwargs["title"]
        self.thumbnail = kwargs.get("thumbnail", None)  # Default to None if missing
        self.small_thumbnail = kwargs.get("small_thumbnail", None)  # Default to None if missing
        self.canonical_volume_link = kwargs.get("canonical_volume_link", None)
        self.links = kwargs["links"]
        self.isbn = kwargs.get("isbn", [])
        self.description = kwargs.get("description", None)
        self.is_folder = kwargs.get("is_folder", False)
        self._data = kwargs

    def get(self, key):
        return self._data.get(key, None)

    def set(self, key, value):
        self.validate(key, value)
        self._data[key] = value

    def to_dict(self):
        return {
            "title": self.title,
            "isbn": self.isbn,
            "small_thumbnail": self.small_thumbnail,
            "canonical_volume_link": self.canonical_volume_link,
            "links": [link.to_dict() for link in self.links],
            "description": self.description,
        }
