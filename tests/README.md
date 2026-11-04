# Running Tests

The tests run without Home Assistant installed. `conftest.py` replaces the Home Assistant modules with mocks before the integration is imported.

## Setup

```bash
uv venv .venv
uv pip install -r requirements-dev.txt
```

Or with the standard library: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`.

## Running Tests

```bash
.venv/bin/python -m pytest -q
```

Any `tests/test_*.py` file is collected automatically. For coverage, run `.venv/bin/python -m pytest --cov=custom_components.bosch_ebike`.

## Test Files

- `test_api_errors.py` - Request failures and timeouts on optional endpoints (location, state of charge) are quiet and don't fail the update
- `test_auth_input.py` - Extracting the authorization code from a pasted redirect URL, including Bosch `error=` redirects and Windows `^` escaping
- `test_bike_profile.py` - Bike lists and profiles come from the v2 bike profile API, with the v1 fallback (see [docs/BIKE_PROFILE_API.md](../docs/BIKE_PROFILE_API.md))
- `test_coordinator_logic.py` - Combining bike profile and state-of-charge data when fields are missing or `null`, e.g. for users without Flow+ ([#4](https://github.com/Phil-Barker/hass-bosch-ebike/issues/4))
- `test_picture.py` - Scaling the Bosch bike picture so the whole bike fits in Home Assistant's round entity picture
- `test_coordinator.py.disabled` - Full coordinator tests that need real Home Assistant modules; not collected

## Writing API Tests

Mock the `aiohttp` session rather than the network. `test_bike_profile.py` has a `FakeResponse` and a `make_api(routes)` helper that answer requests by endpoint, and `test_api_errors.py` shows how to make every request raise.

The config flow has no tests yet: the Home Assistant mocks can't build `ConfigFlow` subclasses, so config flow changes need a manual check in Home Assistant (see [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md)).
