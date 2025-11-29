# Running Tests

These tests verify that the integration handles missing API fields gracefully, particularly for users who have ConnectModule but not Flow+ subscription.

## Setup

Install test dependencies:

```bash
pip install -r requirements-dev.txt
```

## Running Tests

### Simple Logic Tests (Recommended)

The simplest tests that don't require Home Assistant:

```bash
pytest tests/test_coordinator_logic.py
```

These tests verify the core data combination logic works correctly with None values.

### Full Integration Tests

To test the full coordinator class (requires Home Assistant mocks):

```bash
pytest tests/test_coordinator.py
```

Note: These tests use mocks for Home Assistant dependencies, but may have import issues depending on your environment.

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=custom_components.bosch_ebike
```

## Test Coverage

The tests verify:

1. **None connectedModule handling** - When API returns `null` for `connectedModule` (users without Flow+), the integration should not crash
2. **Missing fields** - Various optional fields that might be missing from the API response
3. **Empty arrays** - Empty batteries array handling
4. **None lock field** - Lock field that might be null
5. **None numberOfFullChargeCycles** - Charge cycles field that might be null

These tests specifically address GitHub issue #4 where users without Flow+ subscription were experiencing `AttributeError: 'NoneType' object has no attribute 'get'` errors.

## Test Files

- `test_coordinator_logic.py` - Standalone tests that verify the data combination logic directly (no Home Assistant dependencies)
- `test_coordinator.py` - Full integration tests with Home Assistant mocks
- `conftest.py` - Pytest configuration that mocks Home Assistant modules
