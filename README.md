# google-books-api-sandbox

## Quickstart

```bash
docker build . -t teenyopds
```

```bash
docker run -p 5000:5000 \
  -e GOOGLE_BOOKS_API_KEY=${GOOGLE_BOOKS_API_KEY} \
  -v /path/to/content:/library \
  readops
```

For example:

```bash
docker run -p 5000:5000 -v /Users/admin/Documents/07_books:/library readops
```

Navigate to `http://localhost:5000/catalog` to view OPDS the catalog.
