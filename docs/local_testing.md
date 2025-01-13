# Local testing

To test locally you can run the following command:

```bash
python3 main.py \
  --GOOGLE_BOOKS_API_KEY=${GOOGLE_BOOKS_API_KEY} \
  --CONTENT_BASE_DIR=${CONTENT_BASE_DIR} \
  --DEBUG=True \
  --CATALOG_TEST_PAYLOAD=${CATALOG_TEST_PAYLOAD}
```

Define the `/catalog` endpoint as follows to avoid excessive calls to the API:

```python
import json
import os

@app.route("/catalog")
@app.route("/catalog/<path:path>")
@auth.login_required
def catalog(path=""):
    view_mode = request.args.get("view", "list")  # default to 'list' view
    c = fromdir(request.root_url, request.url, config.CONTENT_BASE_DIR, path)

    # Read the catalog entries from the sample JSON payload
    catalog_entries = []
    try:
        with open('./docs/sample_payloads/catalog_entries.json', 'r') as json_file:
            catalog_entries = json.load(json_file)
            print(f"Catalog entries loaded from file: {len(catalog_entries)} entries found.")
    except Exception as e:
        print(f"Error reading catalog entries from file: {e}")
    
    # You can still include any processing logic if needed
    # For example, you might want to do additional transformations or checks on catalog_entries.

    return c.render(view_mode=view_mode, catalog_entries=catalog_entries, loading=True)
```
