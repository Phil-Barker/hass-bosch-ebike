# AGENTS.md

Guidance for coding agents working on this repository. Human contributors should start with [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Project

A Home Assistant custom integration (`bosch_ebike`, distributed via HACS) for Bosch eBike Flow bikes with a ConnectModule. It polls Bosch's undocumented cloud API every 5 minutes. Everything about the API is reverse engineered, so treat observed behavior as the spec and document what you learn in `docs/`.

## Layout

| Path | Purpose |
|---|---|
| `custom_components/bosch_ebike/api.py` | Bosch API client: OAuth (PKCE), requests, endpoint wrappers |
| `custom_components/bosch_ebike/coordinator.py` | Polls the API and combines profile + state-of-charge + location data |
| `custom_components/bosch_ebike/config_flow.py` | Setup: paste the redirect URL, exchange the code, pick a bike |
| `custom_components/bosch_ebike/{sensor,binary_sensor,device_tracker}.py` | Entities, all read from coordinator data |
| `custom_components/bosch_ebike/strings.json`, `translations/en.json` | UI text. Keep the two files identical |
| `tests/` | Pytest suite with mocked Home Assistant (see `tests/README.md`) |
| `docs/` | User guides and API notes |
| `README.md`, `info.md` | Must stay in the root: GitHub/HACS show them. `info.md` mirrors the README features |
| `exploration/` | Gitignored local API exploration, including live tokens. Never commit or quote from it |

`requirements.txt` is for the local exploration scripts, not the integration. The integration has no pip requirements (`manifest.json` `requirements: []`).

## Tests

```bash
uv venv .venv && uv pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

- Home Assistant is **not** installed. `tests/conftest.py` mocks the `homeassistant.*` modules, so anything you import from Home Assistant must exist in those mocks.
- New `tests/test_*.py` files are collected automatically.
- For API tests, use the `FakeResponse` / `make_api(routes)` helpers in `tests/test_bike_profile.py` rather than real requests.
- The config flow can't be unit tested (the mocks can't build `ConfigFlow` subclasses). Say in the PR that it needs a manual check in Home Assistant.
- GitHub CI runs only HACS and Hassfest validation, not pytest. Run the tests locally and confirm new tests fail without your fix.

## Bosch API

- Hosts: `obc-rider-profile.prod.connected-biking.cloud` (bike profiles, state of charge) and `theft-detection.prod.connected-biking.cloud` (location).
- Bike lists and profiles use **v2** (`/v2/bike-profile`), converted to the v1 `{"data": {"id", "type", "attributes"}}` shape, with a v1 fallback. v1 can omit bikes. See [docs/BIKE_PROFILE_API.md](docs/BIKE_PROFILE_API.md).
- `_api_request` returns `None` on 404 and raises `BoschEBikeAPIError` for other failures, including timeouts. It only logs at debug level, so the caller decides whether a failure is an error.
- Optional data (state of charge, location) must not fail the coordinator update. Return `None` and let the entity show as unavailable.
- Many fields are `null` (e.g. `connectedModule` without a ConnectModule or Flow+, and `lock.isLocked` always). Use `(x.get("key") or {})`, never `x["key"]`.
- What sensors can and can't report is in [docs/SENSOR_RELIABILITY.md](docs/SENSOR_RELIABILITY.md).

## Home Assistant Rules

- Hassfest rejects URLs in translation strings. Pass links through `description_placeholders` (see `AUTH_GUIDE_URL` in `const.py`).
- Every new error or abort key needs text in both `strings.json` and `translations/en.json`.
- Never change entity keys, unique IDs or the config entry unique ID (the Bosch bike ID), because existing installs would lose their entities.
- The config flow shows errors on the form so the user can retry. Use `async_abort` only for dead ends.
- `AbortFlow` is an exception. Don't create entries inside a `try` block with a broad `except Exception`.

## Git, PRs and Releases

- Conventional Commits (`fix:`, `feat:`, `docs:`, `chore:`). PRs are squash-merged with the subject `type: summary (#N)`.
- PR descriptions explain the user-visible problem first (quoting the issue), then list the changes as bullets, then `Fixes #N`.
- Issue replies use plain language: what was happening, what fixes it, and what the user should do now.
- Releases:
  1. Merge **all** fixes for the release first.
  2. Open a `chore: bump version to X.Y.Z` PR that changes `version` in `manifest.json`, then merge it.
  3. Run `gh release create vX.Y.Z --target main --title "vX.Y.Z - Summary"` with notes in the style of earlier releases (features, fixes with issue links and thanks, upgrade notes, full changelog link).
  4. Confirm the tag contains everything with `gh api repos/Phil-Barker/hass-bosch-ebike/compare/vX.Y.Z...main` (expect `ahead_by: 0`). v1.1.0 was tagged before its last fix merged.
