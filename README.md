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
    products = ananas.get(
        "/product/api/v1/merchant-integration/products",
        params={"page": 0, "size": 100},
    )
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

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check .
```

## Scope

The official API currently covers authorization, products, warehouses, payments, discounts, orders, and shipments. Endpoint-specific helpers and generated models can be added incrementally while `request`, `get`, `post`, `put`, `patch`, and `delete` keep the entire API accessible today.

This project is not affiliated with or endorsed by Ananas. Ananas names and trademarks belong to their respective owners.

## License

[MIT](LICENSE)

