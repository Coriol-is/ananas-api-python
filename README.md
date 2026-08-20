# Ananas API for Python

An unofficial, typed Python client for the [Ananas merchant API](https://developer.ananas.rs/openapi/reference/overview/), maintained by [Coriol-is](https://github.com/Coriol-is).

The client provides authentication, automatic token renewal, consistent error handling, and direct access to every current or future API endpoint without waiting for a library release.

> **Status:** early development. The public interface may change before `1.0`.

## Install

```bash
pip install ananas-api-python
```

## Quick start

```python
from ananas_api import AnanasClient

with AnanasClient(
    base_url="https://api.qa2.ananastest.com",
    api_key="your-api-key",
    client_id="your-client-id",
    client_secret="your-client-secret",
) as ananas:
    products = ananas.products.get_products(page=0, size=100)
    for product in products:
        print(product.id, product.name, product.stock_level)
```

You can also supply an existing bearer token:

```python
client = AnanasClient(base_url="https://your-ananas-api-host", access_token="your-token")
orders = client.get("/order/api/v1/merchant-integration/orders")
client.close()
```

The base URL is explicit because Ananas provides environment-specific hosts. The URL above is the QA server currently published in the OpenAPI specification; use the host assigned to your merchant account in production.

## Authentication

For client-credentials authentication, provide `api_key`, `client_id`, and `client_secret`. The library calls `/iam/api/v1/auth/token` with the documented `CLIENT_CREDENTIALS` grant and `public_api/full_access` scope, caches the bearer token, and renews it before expiration.

Credentials are never read implicitly. Load them from environment variables or a secret manager and pass them to the client.

## Errors

Non-successful responses raise `AnanasAPIError`, which exposes `status_code`, `response`, and the parsed response body when available. Authentication failures raise `AnanasAuthenticationError`.

## Named APIs and typed models

All operations and component schemas in the published Ananas OpenAPI 1.0.0
document have typed coverage:

- `client.products` — product listing/import/update, product types, and EAN checks
- `client.discounts` — schedule, update, query, and cancel discounts
- `client.payments` — warehouses, invoices, corrections, prices, and document URLs

Request models validate field types, identifiers, enums, date formats, date
ranges, page sizes, and documented list limits before sending a request.
Responses are parsed into Pydantic models with Python-friendly names while
preserving the API's JSON aliases.

```python
from ananas_api.models.products import ProductRequest

result = ananas.products.import_or_update_products(
    ProductRequest(
        name="Example product",
        ean="8600000000000",
        sku="SKU-001",
        stockLevel=10,
        basePrice=1999.0,
    )
)
```

Product collection endpoints also provide automatic pagination:

```python
for product in ananas.products.iter_products(size=250):
    print(product.sku)
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
ruff format --check .
```

## Releasing

Releases are automated from version tags. Update `project.version` in
`pyproject.toml`, merge the change, and push a matching tag such as `v0.2.0`.
The release workflow verifies the tag, builds and validates the source and
wheel distributions, adds build-provenance attestations, attaches the files to
a GitHub Release, and publishes them to PyPI using trusted publishing.

Before the first release, configure a PyPI trusted publisher for this
repository with workflow `release.yml` and environment `pypi`. GitHub Packages
does not provide a PyPI-compatible package registry, so installable Python
packages are published to PyPI while GitHub hosts the signed release assets.

## Scope

The published OpenAPI document currently covers authorization, products,
warehouses, payments, and discounts. The lower-level `request`, `get`, `post`,
`put`, `patch`, and `delete` methods remain available for forward compatibility
with endpoints added before the next library release.

This project is not affiliated with or endorsed by Ananas. Ananas names and trademarks belong to their respective owners.

## License

[MIT](LICENSE)
