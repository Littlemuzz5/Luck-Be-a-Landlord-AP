# Live update notes

The APWorld client already updates `ap_state.json` whenever AP receives items/checks. The normal generated LBAL mod folder cannot guarantee true in-run updates because LBAL can cache mod data after load.

To avoid restarting the game after every AP item, patch the running Godot game so the symbol/item/essence choice builders call the bridge filters:

```gdscript
symbols_to_choose_from = APLivePoolBridge.filter_symbol_list(symbols_to_choose_from)
items_to_choose_from = APLivePoolBridge.filter_item_list(items_to_choose_from)
essences_to_choose_from = APLivePoolBridge.filter_essence_list(essences_to_choose_from)
```

Add `docs/LuckBeALandlordGodotBridge.gd` as an Autoload named `APLivePoolBridge`, or attach it to a node that always exists.

The patched `Client.py` writes both raw received unlocks and live active pools:

- `received_unlocked_symbols/items/essences`: everything AP has sent
- `unlocked_symbols/items/essences`: the pool the game should use now
- `live_pool.symbol_types/item_types/essence_types`: internal LBAL type IDs for direct filtering
- `live_pool.always_allowed_symbol_types`: starting symbols, dud/base/empty, and AP Check when needed

If `unlockable_chance_boost` is on, these live fields follow the tracker's possible Send checks, so already-sent first-get symbols/items/essences are removed again until the next batch becomes possible.
