# Luck be a Landlord Setup Guide

1. Put the `luck_be_a_landlord` folder into `Archipelago-main/worlds/`.
2. Generate a YAML for `Luck be a Landlord`.
3. Choose your floor goal options.
4. Generate the Archipelago seed.
5. Use your Luck be a Landlord mod/client to connect to the Archipelago server.

## Important client behavior

When AP sends an item like `Unlock Symbol: Coin`, the mod/client should unlock that content in-game.

When the player first gets a symbol/item/essence in-game, the mod/client should send the matching location check.

Example:

- player first gets `Coin`
- client sends `First Get Symbol: Coin`

## Floor goals

The client should read `goal_floors` and `goal_requirements` from slot data.

Requirement values:

- `beat_payment_12`
- `beat_payment_12`

When the requirement is met, send the matching floor goal location from `goal_locations`.

## DeathLink

The client should read the `deathlink` object from slot data.

`mode` can be:

- `off`
- `next_payment`
- `end_run`

`receive_chance_percent` controls whether an incoming DeathLink triggers.

`receive_threshold` controls how many incoming DeathLinks must be received before triggering.

`send_threshold` controls how many local run-ending failures must happen before sending DeathLink to other players.

## Logic / spheres

Sphere 1 starts with exactly these checks:

- `Payment 1`
- `AP Check 1`
- `AP Check 2`
- `AP Check 3`
- `AP Check 4`
- `AP Check 5`
- `AP Check 6`

All `First Get Symbol/Item/Essence` checks require the matching Archipelago unlock item.
For example, `First Get Symbol: Coin` requires `Unlock Symbol: Coin`.


## Item bundles

The APWorld can bundle multiple unlocks into one Archipelago item.

Options:

- `item_bundles`: `off` or `on`
- `item_bundle_size`: maximum unlocks per bundle, from 2 to 10
- `two_item_bundles`: forces bundles to 2 unlocks each when enabled

Bundle items are named like `Unlock Bundle 1`, `Unlock Bundle 2`, etc.
The exact unlocks inside each bundle are sent in `slot_data` under `item_bundles`.
When the client receives a bundle item, it should unlock every listed symbol/item/essence in that bundle.

First-get logic also understands bundles. For example, if `Unlock Symbol: Coin` is inside `Unlock Bundle 3`, then `First Get Symbol: Coin` is logically unlocked by receiving `Unlock Bundle 3`.


## Included client

This APWorld includes a **Luck be a Landlord Client** launcher component. After installing the `.apworld` and restarting Archipelago Launcher, it should appear in the launcher list.

The client communicates with the game/mod through JSON files in:

```txt
%LOCALAPPDATA%\LuckBeALandlordAP
```

The client writes `ap_state.json`. The game/mod should read this file to see received unlocks, bundled unlock contents, checked locations, and DeathLink data.

The game/mod can send checks by writing `checks_to_send.json`, for example:

```json
{
  "locations": ["Payment 1", "AP Check 1", "First Get Symbol: Coin"]
}
```

The game/mod can send DeathLink by writing `deathlink_send.json`, for example:

```json
{
  "cause": "Luck be a Landlord run ended"
}
```

When the client writes `deathlink_receive.json`, the game/mod should apply the DeathLink effect, then write `deathlink_ack.json` to clear the pending DeathLink.

## Direct game mod bridge behavior

The Luck be a Landlord Client writes the current AP-controlled game state to:

```text
%LOCALAPPDATA%\LuckBeALandlordAP\ap_state.json
```

The game mod must read this file and apply these rules:

- Lock every symbol and item unless it appears in `unlocked_symbols`, `unlocked_items`, or `unlocked_essences`.
- Only show floors listed in `allowed_floors`.
- Hide/disable floors listed in `hidden_floors`.
- Give each AP unlock only once.
- Send game checks by writing `checks_to_send.json` into the same folder.

A starter Godot bridge template is included at:

```text
luck_be_a_landlord/docs/LuckBeALandlordGodotBridge.gd
```

This template still needs to be connected to the real Luck be a Landlord symbol/item/floor functions.


Optional multi-floor goal setting:

```yaml
Luck be a Landlord:
  floors_required: 1  # 0 = random, values above selected floor count are clamped
```


### Symbol hints

In the Luck be a Landlord Archipelago client, use `/hint_symbol Symbol Name` to request a server hint for that symbol unlock. Example: `/hint_symbol King Midas`. If item bundles are enabled, the command hints the bundle containing that symbol.

### Force a symbol into sphere 1

Use `force_sphere_one_symbols` to lock one or more symbol unlocks into AP Check 1-10.

```yaml
Luck be a Landlord:
  force_sphere_one_symbols:
    - Crab
    - Cultist
```

If item bundles are enabled, the bundle containing the forced symbol is placed in sphere 1 instead.

## Filler items

AP Check filler rewards now use the built-in filler item names:

- Strawberry
- Progressive Filler
- Progressive Nothing

Custom YAML filler names were removed so filler rewards stay fixed and tracker-safe.


## V8 update

- DeathLink can be enabled with `deathlink: on`. Incoming DeathLinks end the current run. Failing to pay rent sends a DeathLink.
- DeathLink options: `deathlink_receive_chance`, `deathlink_receive_threshold`, and `deathlink_send_threshold`.
- Symbol, item, and essence unlock rewards are marked as Useful in Archipelago. Floor unlocks, Raspberry, and Progressive AP Checks remain Progression.
