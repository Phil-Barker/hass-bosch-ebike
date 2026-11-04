# Bike Profile API: v1 vs v2

The integration reads each bike's details (batteries, drive unit, ConnectModule, odometer, lock and alarm settings) from the Bosch **bike profile** API. Bosch serves it in two versions. Since v1.1.1 the integration uses v2 and falls back to v1.

Both versions are undocumented and were found by reverse engineering, so everything below is based on observed behavior and may change.

## Summary

- **v1 can leave bikes out.** On some accounts `/v1/bike-profile` lists fewer bikes than the Flow app shows, and `/v1/bike-profile/{id}` returns 404 for the missing ones. Those bikes could never be added to Home Assistant ([#35](https://github.com/Phil-Barker/hass-bosch-ebike/issues/35)).
- **v2 returns every bike** on the account, with the same fields and values as v1.
- **Only the shape differs.** v1 wraps each bike in a JSON:API resource (`{"data": {"id", "type", "attributes"}}`). v2 returns the bike object directly, and the list is a plain JSON array.
- **Bike IDs are the same** in both versions, so existing config entries keep working after the switch.
- **Only bike profiles have a v2.** State of charge and the rider profile stay on v1.

## Endpoints

Base URL: `https://obc-rider-profile.prod.connected-biking.cloud`

| Purpose | v1 | v2 |
|---|---|---|
| List bikes | `GET /v1/bike-profile` | `GET /v2/bike-profile` |
| One bike | `GET /v1/bike-profile/{id}` | `GET /v2/bike-profile/{id}` |
| State of charge | `GET /v1/state-of-charge/{id}` | none (`/v2/state-of-charge/{id}` returns 403) |
| Rider profile | `GET /v1/profile` | none (`/v2/profile` returns 403) |

All requests use the same OAuth access token (`Authorization: Bearer ...`). The token's audience list includes `obc-rider-profile`, which covers both versions.

## Response Shapes

The examples are trimmed, and the values are only illustrative.

### List bikes

v1 wraps the bikes in `data`. Each bike is a resource whose fields live in `attributes`:

```json
{
  "data": [
    {
      "id": "BIKE_ID",
      "type": "...",
      "attributes": {
        "id": "BIKE_ID",
        "brandName": "Cube",
        "batteries": [{ "batteryLevel": 80, "totalEnergy": 750 }],
        "driveUnit": { "productName": "Performance Line CX", "lock": { "isEnabled": true } },
        "connectedModule": { "isAlarmFeatureEnabled": true },
        "remoteControl": { },
        "mediaAssets": { }
      },
      "relationships": {},
      "links": {}
    }
  ],
  "links": {}
}
```

v2 returns a plain array of the same bike objects:

```json
[
  {
    "id": "BIKE_ID",
    "brandName": "Cube",
    "batteries": [{ "batteryLevel": 80, "totalEnergy": 750 }],
    "driveUnit": { "productName": "Performance Line CX", "lock": { "isEnabled": true } },
    "connectedModule": { "isAlarmFeatureEnabled": true },
    "remoteControl": { },
    "mediaAssets": { }
  }
]
```

### One bike

v1 returns `{"data": {"id", "type", "attributes"}, "links": {}}`. v2 returns the bike object on its own, the same as one entry of the v2 list.

### Fields

For a bike that both versions return, the v2 object has exactly the same keys and values as v1's `attributes`. Checked in November 2026 by comparing the full responses for the same bike. Top-level keys include:

`id`, `brandName`, `createdAt`, `batteries`, `driveUnit`, `connectedModule`, `remoteControl`, `headUnit`, `antiLockBrakeSystem`, `bleComponents`, `mediaAssets`, `collectionTime`

Many of these can be `null`. For example, `connectedModule` is `null` for a bike without a ConnectModule, so code must handle missing or `null` values (see `tests/test_coordinator_logic.py`).

## Which Bikes v1 Leaves Out

There is no known rule yet. What has been seen so far:

| Account | Bikes in the Flow app | v1 list | v2 list | Missing from v1 |
|---|---|---|---|---|
| Reporter of [#35](https://github.com/Phil-Barker/hass-bosch-ebike/issues/35) | 2 | 1 | 2 | The older bike (added January 2026) |
| Maintainer | 2 | 1 | 2 | The newer bike (added October 2026, no ConnectModule) |

v1 doesn't paginate: `links` is empty, and paging parameters such as `?page[size]=50` still return one bike. It isn't simply the oldest or newest bike being dropped. If you find a pattern, please add it here.

## Benefits of v2

- **Every bike can be added.** This is the main reason for the switch. A bike missing from v1 can't be set up at all, and with a single listed bike the config flow auto-selects it and never offers a choice.
- **Profiles load for every bike.** v1 returns 404 for the profiles of bikes it leaves out, so the coordinator would fail on every update.
- **A simpler payload.** There is no JSON:API wrapper to unpack.
- **No data is lost.** The fields are identical, so no sensors change.

## Caveats

- **Undocumented.** Bosch could change or remove v2 without notice. That's why the integration keeps the v1 fallback.
- **Not checked on every account.** v2 has been confirmed on two accounts so far: the reporter of #35 (in the Netherlands) and the maintainer's.
- **Other data still uses v1.** v2 doesn't fix missing live data. Live state of charge (`/v1/state-of-charge/{id}`) needs a ConnectModule and returns 404 without one, whichever bike profile version listed the bike.

## How the Integration Uses It

Implemented in `custom_components/bosch_ebike/api.py` and covered by `tests/test_bike_profile.py`.

- **Converted to the v1 shape.** `get_bikes()` and `get_bike_profile()` call v2 first and wrap the result in the v1 shape (`_v2_bike_to_v1_resource`), so the coordinator and config flow still read `bike["attributes"]` and `profile["data"]["attributes"]`.
- **When v1 is used.** The integration falls back to v1 if v2 returns 404, fails, or returns no bikes (or a bike without an `id`).
- **Auth errors aren't retried.** `BoschEBikeAuthError` is raised straight away, because v1 would fail the same way.
- **The v2 error is preferred.** If v2 fails for a bike and v1 returns 404, the v2 error is raised. v1's 404 is expected for bikes it leaves out and would hide the real failure.

## Checking an Account Yourself

With a valid access token in `$TOKEN`:

```bash
BASE=https://obc-rider-profile.prod.connected-biking.cloud

# Number of bikes in each version
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/v1/bike-profile" | jq '.data | length'
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/v2/bike-profile" | jq 'length'

# Bike IDs in each version
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/v1/bike-profile" | jq -r '.data[].id'
curl -s -H "Authorization: Bearer $TOKEN" "$BASE/v2/bike-profile" | jq -r '.[].id'
```

Full responses contain component serial numbers and other identifying details. Remove them before sharing output in an issue.

## History

- **Up to v1.1.0:** v1 only.
- **v1.1.1:** v2 with v1 fallback ([#36](https://github.com/Phil-Barker/hass-bosch-ebike/pull/36), fixes [#35](https://github.com/Phil-Barker/hass-bosch-ebike/issues/35)). Thanks [@hjkolthof](https://github.com/hjkolthof) for the report and the patch it was based on.
