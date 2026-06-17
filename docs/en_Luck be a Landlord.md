# Luck be a Landlord

This APWorld randomizes all supported Luck be a Landlord symbols and normal items as Archipelago unlocks.

Each piece of content also has a matching first-get check:

- `First Get Symbol: Coin`
- `First Get Item: Black Pepper`
- `First Get Essence: Black Pepper Essence`

The filler item is named `Progressive Filler`.

## Floor goals

The goal can be one floor, a random floor, multiple chosen floors, or multiple random floors.

Floors 1-10 require the client/mod to send the floor goal check after payment 12 is beaten.
Payment 13 is disabled in this APWorld because it can be unstable in-game. Floor goals use the normal victory/floor-clear detection instead.

The generated slot data includes:

- `goal_floors`
- `goal_locations`
- `goal_requirements`

## DeathLink

DeathLink behavior is controlled by slot data. The client/mod should read the `deathlink` object.

Modes:

- `off`
- `next_payment`
- `end_run`

Extra DeathLink settings:

- receive chance percent
- received DeathLinks needed before triggering
- local deaths/failures needed before sending

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


Optional multi-floor goal setting:

```yaml
Luck be a Landlord:
  floors_required: 1  # 0 = random, values above selected floor count are clamped
```


### Symbol hints

In the Luck be a Landlord Archipelago client, use `/hint_symbol Symbol Name` to request a server hint for that symbol unlock. Example: `/hint_symbol King Midas`. If item bundles are enabled, the command hints the bundle containing that symbol.

## Force Sphere One Symbols

`force_sphere_one_symbols` can force selected symbol unlocks into sphere 1, meaning AP Check 1-10. Example:

```yaml
force_sphere_one_symbols:
  - Crab
```

With item bundles enabled, the bundle containing that symbol is forced into sphere 1.


## V8 update

- DeathLink can be enabled with `deathlink: on`. Incoming DeathLinks end the current run. Failing to pay rent sends a DeathLink.
- DeathLink options: `deathlink_receive_chance`, `deathlink_receive_threshold`, and `deathlink_send_threshold`.
- Symbol, item, and essence unlock rewards are marked as Useful in Archipelago. Floor unlocks, Raspberry, and Progressive AP Checks remain Progression.
