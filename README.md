# google-books-api-sandbox

## Quickstart

### Local development

```bash
python3 main.py \
  --google-books-api-key=${GOOGLE_BOOKS_API_KEY} \
  --library=/path/to/content
```

For example:

```bash
python3 main.py \
  --google-books-api-key=AIzaSyD1J1J1J1J1J1J1J1J1J1J1J1J1J1J1 \
  --library=/Users/admin/Documents/07_books
```

### Container

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

### View the catalog

Navigate to `http://localhost:5000/catalog` to view OPDS the catalog.
