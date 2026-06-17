from __future__ import annotations

from typing import Dict, Any, List

from BaseClasses import Item, ItemClassification, Region, Entrance, Tutorial
from worlds.AutoWorld import World, WebWorld

from .Items import (
    LuckItem,
    item_table,
    item_name_groups,
    FILLER_ITEM_NAME,
    FILLER_ITEMS,
    RASPBERRY_ITEM_NAME,
    PROGRESSIVE_AP_CHECKS_ITEM_NAME,
    UNLOCK_ITEMS,
    BUNDLE_ITEMS,
    FLOOR_UNLOCK_ITEMS,
    SYMBOLS,
    NORMAL_ITEMS,
    ESSENCES,
    RARE_SYMBOLS,
    VERY_RARE_SYMBOLS,
    RARE_ITEMS,
    VERY_RARE_ITEMS,
    RARE_ESSENCES,
    VERY_RARE_ESSENCES,
    TRAP_ITEMS,
    BUFF_ITEMS,
)
from .Locations import (
    LuckLocation,
    location_table,
    location_name_groups,
    FILLER_CHECK_LOCATIONS,
    PAYMENT_LOCATIONS,
    SPHERE_ONE_CHECKS,
    FLOOR_GOAL_LOCATIONS,
    FLOOR_PAYMENT_LOCATIONS,
    floor_goal_location_name,
    floor_goal_requirement,
    payment_event_name,
    floor_goal_event_name,
)
from .Options import LuckOptions
from .Rules import set_rules

from worlds.LauncherComponents import components, Component, launch, Type as ComponentType


def launch_client(*args: str) -> None:
    from .Client import launch as launch_luck_client
    launch(launch_luck_client, name="Luck be a Landlord Client", args=args)


components.append(Component(
    "Luck be a Landlord Client",
    game_name="Luck be a Landlord",
    func=launch_client,
    component_type=ComponentType.CLIENT,
    supports_uri=True,
))




BUFF_WEIGHT_OPTION_BY_ITEM_V144 = {
    "Buff: Start With a Destroy Token": "start_destroy_token_buff_weight",
    "Buff: Start With $5": "start_5_dollars_buff_weight",
    "Buff: Start With a Reroll Token": "start_reroll_token_buff_weight",
    "Buff: Choice of Symbols": "choice_symbols_buff_weight",
    "Buff: Start With an Essence Token": "start_essence_token_buff_weight",
}

TRAP_WEIGHT_OPTION_BY_ITEM_V144 = {
    "Trap: Half Money": "half_money_trap_weight",
    "Trap: Force Payment": "force_payment_trap_weight",
    "Trap: Add Dud Symbol": "add_dud_symbol_trap_weight",
}

WEIGHT_VALUE_TO_COUNT_V144 = {
    0: 0,  # none
    1: 1,  # low
    2: 3,  # medium
    3: 6,  # high
}



class LuckWeb(WebWorld):
    tutorials = [Tutorial(
        "Luck be a Landlord Setup Guide",
        "A guide to setting up Luck be a Landlord for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
    )]
    theme = "partyTime"


class LuckBeALandlordWorld(World):
    """
    Luck be a Landlord APWorld.

    Every symbol and normal item is randomized as an Archipelago unlock.
    Essences stay available in-game as vanilla content, but are not AP unlocks
    and do not have First Get checks.
    """

    game = "Luck be a Landlord"
    web = LuckWeb()
    options_dataclass = LuckOptions
    options: LuckOptions

    item_name_to_id = {name: data.code for name, data in item_table.items() if data.code is not None}
    location_name_to_id = {name: data.code for name, data in location_table.items() if data.code is not None}
    item_name_groups = item_name_groups
    location_name_groups = location_name_groups

    topology_present = False
    ut_can_gen_without_yaml = True

    def _get_ut_regen_slot_data(self) -> Dict[str, Any]:
        """Return Universal Tracker re-gen slot_data, even if UT keys it differently.

        Some UT builds key re_gen_passthrough by game name, while others may pass
        the slot data under another key. This helper searches for the LBAL slot
        data instead of only checking self.game, so options like extra_filler_checks,
        chosen floors, floor unlock mode, and Raspberry goal are restored reliably.
        """
        re_gen_passthrough = getattr(self.multiworld, "re_gen_passthrough", {}) or {}
        if not isinstance(re_gen_passthrough, dict):
            return {}

        direct = re_gen_passthrough.get(self.game)
        if isinstance(direct, dict):
            return direct

        for value in re_gen_passthrough.values():
            if isinstance(value, dict) and value.get("game") == self.game:
                return value
            if isinstance(value, dict) and ("check_location_name_to_id" in value or "raspberry_goal" in value):
                return value
        return {}

    def generate_early(self) -> None:
        slot_data = self._get_ut_regen_slot_data()
        if slot_data:
            self._ut_slot_data = slot_data
            slot_options = slot_data.get("options", {}) or {}

            # Older slot_data versions also stored a few options at top level.
            # Use those as fallbacks if the nested options dict is missing.
            for fallback_key in (
                "extra_filler_checks", "starting_symbol_mode", "floor_unlock_mode", "floor_payment_checks",
                "item_bundles", "item_bundle_size", "two_item_bundles",
                "rare_checks", "very_rare_checks", "rare_very_rare_in_game_pool", "item_randomizer", "essence_randomizer", "progressive_ap_checks", "unlockable_chance_boost", "unlockable_chance_weight", "deathlink", "deathlink_receive_chance", "deathlink_receive_threshold", "deathlink_send_threshold", "raspberry_pool", "raspberry_required", "buffs", "buff_percentage", "start_destroy_token_buff_weight", "start_5_dollars_buff_weight", "start_reroll_token_buff_weight", "start_essence_token_buff_weight", "choice_symbols_buff_weight", "traps", "trap_percentage", "half_money_trap_weight", "force_payment_trap_weight", "add_dud_symbol_trap_weight",
            ):
                if fallback_key in slot_data and fallback_key not in slot_options:
                    slot_options[fallback_key] = slot_data[fallback_key]

            # Upgrade old seeds/UT passthrough data: old numeric weight 10 = new boost on.
            if "unlockable_chance_weight" in slot_options and "unlockable_chance_boost" not in slot_options:
                try:
                    slot_options["unlockable_chance_boost"] = int(slot_options.get("unlockable_chance_weight", 1) or 1) >= 10
                except Exception:
                    slot_options["unlockable_chance_boost"] = False

            if "raspberry_goal" in slot_data and isinstance(slot_data.get("raspberry_goal"), dict):
                goal_data = slot_data["raspberry_goal"]
                if "pool" in goal_data and "raspberry_pool" not in slot_options:
                    slot_options["raspberry_pool"] = goal_data["pool"]
                if "required" in goal_data and "raspberry_required" not in slot_options:
                    slot_options["raspberry_required"] = goal_data["required"]

            for key, value in dict(slot_options).items():
                opt = getattr(self.options, key, None)
                if opt is not None:
                    try:
                        setattr(self.options, key, opt.from_any(value))
                    except Exception:
                        # Keep default/local option if an old slot has a value this APWorld no longer accepts.
                        pass
            if "goal_floors" in slot_data:
                self.goal_floors = [int(floor) for floor in slot_data.get("goal_floors", [])]
            if "goal_floors_required" in slot_data:
                self.goal_floors_required = int(slot_data.get("goal_floors_required", 1) or 1)


        if not hasattr(self, "goal_floors"):
            self.goal_floors = self._choose_goal_floors()
        if not hasattr(self, "goal_floors_required"):
            self.goal_floors_required = self._choose_goal_floors_required()
        self.raspberry_pool_count = self._raspberry_pool_count()
        self.raspberry_required_count = self._raspberry_required_count()
        self._build_item_bundles()

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        apartment = Region("Apartment", self.player, self.multiworld)

        enabled_locations = self._enabled_location_names()
        # Real AP check locations. These have integer IDs and can receive randomized items.
        apartment.locations += [
            LuckLocation(self.player, name, location_table[name].code, apartment)
            for name in enabled_locations
        ]

        # Internal event locations. These have no ID, are not sent by the client,
        # and are only used so Archipelago can build logical spheres.
        # Do NOT place event items on real AP checks, or the server will crash
        # with "TypeError: an integer is required" when loading the room.
        apartment.locations += [
            LuckLocation(self.player, payment_event_name(payment), None, apartment)
            for payment in range(1, 13)
        ]
        apartment.locations += [
            LuckLocation(self.player, floor_goal_event_name(floor), None, apartment)
            for floor in self.goal_floors
        ]

        entrance = Entrance(self.player, "Start Game", menu)
        menu.exits.append(entrance)
        entrance.connect(apartment)

        self.multiworld.regions += [menu, apartment]

    def create_items(self) -> None:
        if not hasattr(self, "bundle_name_to_unlocks"):
            self._build_item_bundles()

        enabled_locations = self._enabled_location_names()
        forced_symbol_unlocks = self._forced_sphere_one_symbol_unlocks()

        if self._bundles_enabled():
            item_names = list(self.bundle_name_to_unlocks.keys())
        else:
            # Only create unlock items that have a matching enabled First Get check.
            # This keeps the rule "every unlock has a corresponding check" true.
            # It also fixes reduced-check YAMLs with rare/very rare checks off,
            # where removed First Get locations otherwise left too many unlock
            # items for the number of enabled locations.
            item_names = self._active_unlock_items()

        # Add floor unlock AP items when selected floors are received through checks.
        if self._floor_unlock_mode() == "unlock_through_items":
            # The first selected floor is always available so the player has somewhere to start.
            for floor in list(self.goal_floors)[1:]:
                item_names.append(f"Unlock Floor {int(floor)}")

        progressive_ap_check_count = self._progressive_ap_checks_needed()
        if progressive_ap_check_count > 0:
            # Progressive AP Checks are placed on the first AP Check of each
            # currently open block. This means the player only needs one AP
            # Check from the current block to unlock the next 10 AP Checks:
            # AP Check 1 -> opens 11-20, AP Check 11 -> opens 21-30, etc.
            # They are locked here instead of being randomly filled, otherwise
            # restrictive fill can bury the next AP Check unlock behind a much
            # later Send: check and the tracker looks broken.
            placed_progressive = 0
            for block_index in range(progressive_ap_check_count):
                location_name = f"AP Check {1 + (block_index * 10)}"
                if location_name not in enabled_locations:
                    continue
                location = self.multiworld.get_location(location_name, self.player)
                if location.item is None:
                    location.place_locked_item(self.create_item(PROGRESSIVE_AP_CHECKS_ITEM_NAME))
                    placed_progressive += 1
            remaining_progressive = max(0, progressive_ap_check_count - placed_progressive)
            if remaining_progressive > 0:
                item_names += [PROGRESSIVE_AP_CHECKS_ITEM_NAME] * remaining_progressive

        # Raspberry is the only goal item that can replace normal filler.
        # It does not remove/unplace unlocks, so each unlock can still have a
        # corresponding First Get check even when extra_filler_checks is low.
        raspberry_count = int(getattr(self, "raspberry_pool_count", self._raspberry_pool_count()))
        if raspberry_count > 0:
            item_names += [RASPBERRY_ITEM_NAME] * raspberry_count

        # Force-sphere symbol option places selected unlocks into the earliest
        # open real locations. AP Check locations are allowed here; they are just
        # extra checks and can contain unlocks, Raspberry, Strawberry, or filler.
        if forced_symbol_unlocks:
            available_locations = [
                name for name in enabled_locations
                if self.multiworld.get_location(name, self.player).item is None
            ]
            if self._bundles_enabled():
                forced_items = []
                for unlock_name in forced_symbol_unlocks:
                    bundle_name = getattr(self, "unlock_name_to_bundle", {}).get(unlock_name)
                    if bundle_name and bundle_name not in forced_items:
                        forced_items.append(bundle_name)
            else:
                forced_items = list(forced_symbol_unlocks)

            for location_name, forced_item in zip(available_locations, forced_items):
                if forced_item in item_names:
                    location = self.multiworld.get_location(location_name, self.player)
                    if location.item is None:
                        location.place_locked_item(self.create_item(forced_item))
                        item_names.remove(forced_item)

        enabled_open_count = len([
            name for name in enabled_locations
            if self.multiworld.get_location(name, self.player).item is None
        ])

        # Fill only the remaining surplus locations with filler rewards.
        # V139: optional buffs/traps can replace a percentage of these filler slots.
        # They never replace unlocks, Raspberry, Progressive AP Checks, or floor unlocks.
        filler_slots = max(0, enabled_open_count - len(item_names))
        buff_pool = self._weighted_buff_items_v143() if self._buffs_enabled_v139() else []
        trap_pool = self._weighted_trap_items_v143() if self._traps_enabled_v139() else []
        buff_percent = max(0, min(100, self._option_int_v139("buff_percentage", 0))) if buff_pool else 0
        trap_percent = max(0, min(100, self._option_int_v139("trap_percentage", 0))) if trap_pool else 0
        buff_slots = min(filler_slots, int(round(filler_slots * buff_percent / 100.0)))
        trap_slots = min(max(0, filler_slots - buff_slots), int(round(filler_slots * trap_percent / 100.0)))
        normal_filler_slots = max(0, filler_slots - buff_slots - trap_slots)
        item_names += [self.random.choice(buff_pool) for _ in range(buff_slots)]
        item_names += [self.random.choice(trap_pool) for _ in range(trap_slots)]
        item_names += [self.random.choice(FILLER_ITEMS) for _ in range(normal_filler_slots)]

        # If there are somehow too many items for the enabled location count,
        # remove filler first. Raspberry is a goal item, so do not trim it below
        # the required amount or the seed can generate as unbeatable.
        if len(item_names) > enabled_open_count:
            overflow = len(item_names) - enabled_open_count

            trimmed: List[str] = []
            for item_name in item_names:
                if overflow > 0 and item_name in FILLER_ITEMS:
                    overflow -= 1
                    continue
                trimmed.append(item_name)
            item_names = trimmed

            if overflow > 0:
                required_raspberry = int(getattr(self, "raspberry_required_count", self._raspberry_required_count()) or 0)
                raspberry_seen = 0
                trimmed = []
                for item_name in item_names:
                    if item_name == RASPBERRY_ITEM_NAME:
                        raspberry_seen += 1
                        if overflow > 0 and raspberry_seen > required_raspberry:
                            overflow -= 1
                            continue
                    trimmed.append(item_name)
                item_names = trimmed

            if overflow > 0:
                # Last-resort fallback: make sure generation fails with a clear
                # reason rather than silently deleting progression/unlocks.
                raise Exception(
                    f"Not enough enabled locations for Luck be a Landlord items. "
                    f"Need {overflow} more locations. Increase extra_filler_checks or reduce Raspberry/floor options."
                )

        self.random.shuffle(item_names)
        self.multiworld.itempool += [self.create_item(name) for name in item_names]

    def create_item(self, name: str) -> Item:
        data = item_table[name]
        classification = data.classification

        # V8: symbol/item/essence Unlock items are marked Useful in AP so they
        # do not display as major progression rewards. Floor unlocks, Raspberry,
        # and Progressive AP Checks stay Progression because they directly open
        # AP spheres or the win condition.

        return LuckItem(name, classification, data.code, self.player)

    def create_event(self, name: str) -> Item:
        return LuckItem(name, ItemClassification.progression, None, self.player)

    def get_filler_item_name(self) -> str:
        return FILLER_ITEM_NAME

    def set_rules(self) -> None:
        set_rules(self)

    def fill_slot_data(self) -> Dict[str, Any]:
        # This gives your Godot mod/Python client the exact AP IDs it should use.
        enabled_locations = self._enabled_location_names()
        return {
            "game": self.game,
            "seed_name": self.multiworld.seed_name,
            "player_name": self.player_name,
            "player_id": self.player,
            "options": self.options.as_dict(
                "extra_filler_checks",
                "starting_symbol_mode",
                "goal_mode",
                "chosen_floor",
                "chosen_floors",
                "floors_required",
                "floor_unlock_mode",
                "floor_payment_checks",
                "item_bundles",
                "item_bundle_size",
                "two_item_bundles",
                "force_sphere_one_symbols",
                "rare_checks",
                "very_rare_checks",
                "rare_very_rare_in_game_pool",
                "item_randomizer",
                "essence_randomizer",
                "progressive_ap_checks",
                "unlockable_chance_boost",
                "unlockable_chance_boost_mode",
                "deathlink",
                "deathlink_receive_chance",
                "deathlink_receive_threshold",
                "deathlink_send_threshold",
                "force_payment_trap_counts_deathlink",
                "raspberry_pool",
                "raspberry_required",
                "buffs",
                "buff_percentage",
                "start_destroy_token_buff_weight",
                "start_5_dollars_buff_weight",
                "start_reroll_token_buff_weight",
                "start_essence_token_buff_weight",
                "choice_symbols_buff_weight",
                "traps",
                "trap_percentage",
                "half_money_trap_weight",
                "force_payment_trap_weight",
                "add_dud_symbol_trap_weight",
            ),
            "symbols": SYMBOLS,
            "items": NORMAL_ITEMS,
            "essences": ESSENCES,
            "unlock_item_name_to_id": self.item_name_to_id,
            "item_bundles_enabled": self._bundles_enabled(),
            "item_bundle_size": self._bundle_size() if self._bundles_enabled() else 0,
            "item_bundles": getattr(self, "bundle_name_to_unlocks", {}),
            "unlock_to_bundle": getattr(self, "unlock_name_to_bundle", {}),
            "check_location_name_to_id": {
                name: self.location_name_to_id[name]
                for name in enabled_locations
            },
            "sphere_one_locations": {
                name: self.location_name_to_id[name]
                for name in SPHERE_ONE_CHECKS
                if name in self.location_name_to_id and name in enabled_locations
            },
            "ap_checks_per_payment": 10,
            "progressive_ap_checks_enabled": self._progressive_ap_checks_enabled(),
            "progressive_ap_checks_item_name": PROGRESSIVE_AP_CHECKS_ITEM_NAME,
            "progressive_ap_checks_needed": self._progressive_ap_checks_needed(),
            "max_ap_checks_supported": 200,
            "payment_locations": {
                name: self.location_name_to_id[name]
                for name in PAYMENT_LOCATIONS
                if name in enabled_locations
            },
            "payment_logic_summary": {
                "Payment 1": "appears after AP Check 1-10",
                "Payment 2": "requires Payment 1 Cleared",
                "Payment 3": "requires Payment 2 Cleared",
                "Payment 4": "requires Payment 3 Cleared",
                "Payment 5": "requires Payment 4 Cleared",
                "Payment 6": "requires Payment 5 Cleared",
                "Payment 7": "requires Payment 6 Cleared",
                "Payment 8": "requires Payment 7 Cleared",
                "Payment 9": "requires Payment 8 Cleared",
                "Payment 10": "requires Payment 9 Cleared",
                "Payment 11": "requires Payment 10 Cleared",
                "Payment 12": "requires Payment 11 Cleared",
            },
            "goal_floors": list(self.goal_floors),
            "goal_floors_required": int(getattr(self, "goal_floors_required", len(self.goal_floors))),
            "floor_unlock_mode": self._floor_unlock_mode(),
            "per_floor_payment_checks": self._per_floor_payment_checks(),
            "payment_check_style": "per_floor" if self._per_floor_payment_checks() else "shared",
            "goal_locations": {
                str(floor): self.location_name_to_id[floor_goal_location_name(floor)]
                for floor in self.goal_floors
            },
            "goal_requirements": {
                str(floor): floor_goal_requirement(floor)
                for floor in self.goal_floors
            },
            "deathlink": {
                "enabled": self._deathlink_enabled(),
                "receive_chance_percent": self._deathlink_receive_chance(),
                "receive_threshold": self._deathlink_receive_threshold(),
                "send_threshold": self._deathlink_send_threshold(),
                "receive_action": "end_run",
                "send_on_fail_to_pay": True,
            },
            "deathlink_enabled": self._deathlink_enabled(),
            "filler_item_name": FILLER_ITEM_NAME,
            "filler_item_names": list(FILLER_ITEMS),
            "buffs_enabled": self._buffs_enabled_v139(),
            "buff_percentage": max(0, min(100, self._option_int_v139("buff_percentage", 0))),
            "buff_weights": {item: self._weight_option_value_v144(option_name, 2) for item, option_name in BUFF_WEIGHT_OPTION_BY_ITEM_V144.items()},
            "traps_enabled": self._traps_enabled_v139(),
            "trap_percentage": max(0, min(100, self._option_int_v139("trap_percentage", 0))),
            "trap_weights": {item: self._weight_option_value_v144(option_name, 2) for item, option_name in TRAP_WEIGHT_OPTION_BY_ITEM_V144.items()},
            "raspberry_goal": {
                "enabled": self._raspberry_enabled(),
                "item_name": RASPBERRY_ITEM_NAME,
                "pool": int(getattr(self, "raspberry_pool_count", self._raspberry_pool_count())),
                "required": int(getattr(self, "raspberry_required_count", self._raspberry_required_count())),
            },
            "extra_filler_checks": max(0, min(200, int(self.options.extra_filler_checks.value))),
            "starting_symbol_mode": self._starting_symbol_mode_v141(),
            "spin_ap_checks_mode": self._spin_ap_checks_mode(),
            "progressive_ap_checks_enabled": self._progressive_ap_checks_enabled(),
            "progressive_ap_checks_needed": self._progressive_ap_checks_needed(),
            "starting_symbols": (["Coin", "Flower", "Pearl", "Cherry", "Cat"] if self._spin_ap_checks_mode() else ["AP Check", "AP Check", "AP Check", "AP Check", "AP Check"]),
            "force_sphere_one_symbols": sorted([str(symbol) for symbol in self.options.force_sphere_one_symbols.value], key=str.lower),
            "essences_are_vanilla_available": True,
            "vanilla_rarity_pool": {
                "enabled": self._rare_very_rare_in_game_pool_enabled(),
                "symbols": sorted(set(
                    ([] if (self._rare_checks_enabled() or not self._rare_very_rare_in_game_pool_enabled()) else list(RARE_SYMBOLS))
                    + ([] if (self._very_rare_checks_enabled() or not self._rare_very_rare_in_game_pool_enabled()) else list(VERY_RARE_SYMBOLS))
                )),
                "items": sorted(set(
                    ([] if (self._rare_checks_enabled() or not self._rare_very_rare_in_game_pool_enabled()) else list(RARE_ITEMS))
                    + ([] if (self._very_rare_checks_enabled() or not self._rare_very_rare_in_game_pool_enabled()) else list(VERY_RARE_ITEMS))
                )),
                "essences": sorted(set(
                    ([] if (self._rare_checks_enabled() or not self._rare_very_rare_in_game_pool_enabled()) else list(RARE_ESSENCES))
                    + ([] if (self._very_rare_checks_enabled() or not self._rare_very_rare_in_game_pool_enabled()) else list(VERY_RARE_ESSENCES))
                )),
            },
            "rare_checks_enabled": self._rare_checks_enabled(),
            "very_rare_checks_enabled": self._very_rare_checks_enabled(),
            "rare_very_rare_in_game_pool_enabled": self._rare_very_rare_in_game_pool_enabled(),
            "item_randomizer_enabled": self._item_randomizer_enabled(),
            "essence_randomizer_enabled": self._essence_randomizer_enabled(),
            "unlockable_chance_boost": self._unlockable_chance_boost_enabled(),
            "unlockable_chance_boost_mode": self._unlockable_chance_boost_mode(),
            "unlockable_chance_weight": self._unlockable_chance_weight(),
            "logic_notes": "AP Check 1-10 start open. AP Check 1 contains Progressive AP Checks to open 11-20, AP Check 11 opens 21-30, and so on. Send checks require their matching Unlock item, which keeps external sphere trackers accurate.",
            "diamond_respects_very_rare_checks_v135": True,
        }


    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        # Universal Tracker can regenerate this world from the real slot_data instead of needing a YAML.
        return slot_data

    def _forced_sphere_one_symbol_unlocks(self) -> List[str]:
        """Return forced symbol unlock item names from YAML in deterministic order."""
        forced = getattr(self.options, "force_sphere_one_symbols", None)
        if forced is None:
            return []
        try:
            symbols = sorted({str(symbol) for symbol in forced.value}, key=self._natural_symbol_key)
        except Exception:
            symbols = []
        valid_symbols = set(SYMBOLS)
        return [f"Unlock: {symbol}" for symbol in symbols if symbol in valid_symbols]

    def _option_int_v139(self, option_name: str, default: int = 0) -> int:
        opt = getattr(self.options, option_name, None)
        if opt is None:
            return int(default)
        try:
            return int(opt.value)
        except Exception:
            try:
                return int(opt)
            except Exception:
                return int(default)

    def _option_set_v139(self, option_name: str, valid_values: List[str]) -> List[str]:
        opt = getattr(self.options, option_name, None)
        if opt is None:
            return list(valid_values)
        try:
            raw_values = opt.value
        except Exception:
            raw_values = opt
        try:
            selected = {str(value) for value in raw_values}
        except Exception:
            selected = set()
        valid = set(valid_values)
        return [value for value in valid_values if value in selected and value in valid]

    def _weight_option_value_v144(self, option_name: str, default: int = 2) -> int:
        value = self._option_int_v139(option_name, default)
        if value < 0 or value > 3:
            return default
        return value

    def _individual_weighted_effect_pool_v144(self, base_items: List[str], weight_options_by_item: Dict[str, str]) -> List[str]:
        """Build a weighted pool using one YAML option per buff/trap.

        Example:
            half_money_trap_weight: medium
            force_payment_trap_weight: high
            add_dud_symbol_trap_weight: none

        Choice values are none=0, low=1, medium=2, high=3.
        """
        weighted: List[str] = []
        for item in base_items:
            option_name = weight_options_by_item.get(item)
            weight_value = self._weight_option_value_v144(option_name, 2) if option_name else 2
            count = WEIGHT_VALUE_TO_COUNT_V144.get(weight_value, 3)
            weighted.extend([item] * count)
        return weighted

    def _buffs_enabled_v139(self) -> bool:
        return bool(self._option_int_v139("buffs", 0))

    def _traps_enabled_v139(self) -> bool:
        return bool(self._option_int_v139("traps", 0))

    def _enabled_buff_items_v139(self) -> List[str]:
        return list(BUFF_ITEMS)

    def _enabled_trap_items_v139(self) -> List[str]:
        return list(TRAP_ITEMS)

    def _weighted_effect_pool_v143(self, base_pool: List[str], low_option: str, medium_option: str, high_option: str) -> List[str]:
        """Turn enabled buff/trap items into a weighted random pool.

        Weights:
        low = 1
        medium = 3
        high = 6

        Items not listed in any tier stay medium so old YAMLs keep working.
        If an item is listed in more than one tier, high wins over medium, and
        medium wins over low.
        """
        base_items = [str(item) for item in base_pool]
        base_set = set(base_items)
        if not base_items:
            return []

        weights = {item: 3 for item in base_items}

        for item in self._option_set_v139(low_option, base_items):
            if item in base_set:
                weights[item] = 1
        for item in self._option_set_v139(medium_option, base_items):
            if item in base_set:
                weights[item] = 3
        for item in self._option_set_v139(high_option, base_items):
            if item in base_set:
                weights[item] = 6

        weighted: List[str] = []
        for item in base_items:
            weighted.extend([item] * max(1, int(weights.get(item, 3))))
        return weighted

    def _weighted_buff_items_v143(self) -> List[str]:
        # V144: use one option per buff, e.g. start_5_dollars_buff_weight: high.
        # Set an individual buff weight to "none" to disable it.
        return self._individual_weighted_effect_pool_v144(
            self._enabled_buff_items_v139(),
            BUFF_WEIGHT_OPTION_BY_ITEM_V144,
        )

    def _weighted_trap_items_v143(self) -> List[str]:
        # V144: use one option per trap, e.g. half_money_trap_weight: medium.
        # Set an individual trap weight to "none" to disable it.
        return self._individual_weighted_effect_pool_v144(
            self._enabled_trap_items_v139(),
            TRAP_WEIGHT_OPTION_BY_ITEM_V144,
        )

    @staticmethod
    def _natural_symbol_key(name: str) -> tuple:
        return (str(name).lower(), str(name))

    def _bundles_enabled(self) -> bool:
        return int(self.options.item_bundles.value) == 1

    def _bundle_size(self) -> int:
        if bool(int(self.options.two_item_bundles.value)):
            return 2
        return max(2, min(10, int(self.options.item_bundle_size.value)))


    def _ap_unlock_allowed_by_rarity_options(self, name: str) -> bool:
        """True if an unlock should be created as an AP randomizer item.

        When rare_checks/very_rare_checks are off, that content stays available
        as vanilla LBAL pool content, but it should not become an AP Unlock item
        or a Send check.
        """
        if not self._rare_checks_enabled() and (
            name in RARE_SYMBOLS or name in RARE_ITEMS or name in RARE_ESSENCES
        ):
            return False
        if not self._very_rare_checks_enabled() and (
            name in VERY_RARE_SYMBOLS or name in VERY_RARE_ITEMS or name in VERY_RARE_ESSENCES
        ):
            return False
        return True

    def _candidate_unlock_items(self) -> List[str]:
        """All unlock item names allowed by the current randomizer settings."""
        matryoshka_extra = {"Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5"}
        active: List[str] = []
        for symbol in SYMBOLS:
            if symbol in matryoshka_extra:
                continue
            if self._ap_unlock_allowed_by_rarity_options(symbol):
                active.append(f"Unlock: {symbol}")
        if self._item_randomizer_enabled():
            for item in NORMAL_ITEMS:
                if self._ap_unlock_allowed_by_rarity_options(item):
                    active.append(f"Unlock: {item}")
        if self._essence_randomizer_enabled():
            for essence in ESSENCES:
                if self._ap_unlock_allowed_by_rarity_options(essence):
                    active.append(f"Unlock: {essence}")
        return active

    def _active_unlock_items(self) -> List[str]:
        """Unlock items that have a matching enabled First Get location.

        Bundles off: an unlock only exists if its matching Send location exists.
        This keeps the rule true that every unlock has a corresponding check.
        Item/Essence randomizer options decide whether item/essence unlocks and
        checks exist at all; when off, that content is vanilla in-game.
        """
        enabled = set(self._enabled_location_names())
        active: List[str] = []
        matryoshka_extra = {"Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5"}
        for symbol in SYMBOLS:
            if symbol in matryoshka_extra:
                continue
            if f"Send: {symbol}" in enabled:
                active.append(f"Unlock: {symbol}")
        if self._item_randomizer_enabled():
            for item in NORMAL_ITEMS:
                if f"Send: {item}" in enabled:
                    active.append(f"Unlock: {item}")
        if self._essence_randomizer_enabled():
            for essence in ESSENCES:
                if f"Send: {essence}" in enabled:
                    active.append(f"Unlock: {essence}")
        return active

    def _build_item_bundles(self) -> None:
        """Build deterministic per-seed AP item bundles.

        Bundle items are generic AP items like "Unlock Bundle 1".
        The actual unlocks contained in each bundle are sent to the client in slot_data.
        """
        self.bundle_name_to_unlocks: Dict[str, List[str]] = {}
        self.unlock_name_to_bundle: Dict[str, str] = {}

        slot_data = getattr(self, "_ut_slot_data", {}) or {}
        if slot_data.get("item_bundles"):
            self.bundle_name_to_unlocks = {
                str(bundle_name): [str(unlock) for unlock in unlocks]
                for bundle_name, unlocks in dict(slot_data.get("item_bundles", {})).items()
            }
            self.unlock_name_to_bundle = {
                str(unlock): str(bundle_name)
                for bundle_name, unlocks in self.bundle_name_to_unlocks.items()
                for unlock in unlocks
            }
            return

        if not self._bundles_enabled():
            return

        unlocks = list(self._candidate_unlock_items())
        self.random.shuffle(unlocks)
        size = self._bundle_size()

        for index in range(0, len(unlocks), size):
            bundle_number = (index // size) + 1
            bundle_name = BUNDLE_ITEMS[bundle_number - 1]
            contents = unlocks[index:index + size]
            self.bundle_name_to_unlocks[bundle_name] = contents
            for unlock_name in contents:
                self.unlock_name_to_bundle[unlock_name] = bundle_name

    def has_unlock_access(self, state, unlock_name: str) -> bool:
        """Logic helper used by Rules.py.

        Without bundles, a First Get check requires its matching Unlock item.
        With bundles, it requires the bundle that contains that unlock.
        """
        if state.has(unlock_name, self.player):
            return True
        bundle_name = getattr(self, "unlock_name_to_bundle", {}).get(unlock_name)
        return bool(bundle_name and state.has(bundle_name, self.player))

    def _choose_goal_floors(self) -> List[int]:
        mode = int(self.options.goal_mode.value)

        if mode == 0:  # chosen_floor
            return [int(self.options.chosen_floor.value)]

        if mode == 2:  # chosen_floors
            chosen = sorted({int(floor) for floor in self.options.chosen_floors.value})
            return chosen or [int(self.options.chosen_floor.value)]

        # random_floors was removed. If an old YAML still has the old value,
        # fall back safely to chosen_floor instead of generating unwanted pages.
        return [int(self.options.chosen_floor.value)]

    def _choose_goal_floors_required(self) -> int:
        floors = list(getattr(self, "goal_floors", []) or [int(self.options.chosen_floor.value)])
        max_needed = max(1, len(floors))
        raw = int(self.options.floors_required.value)
        if raw <= 0:
            return self.random.randint(1, max_needed)
        return max(1, min(raw, max_needed))

    def _floor_unlock_mode(self) -> str:
        return "unlock_through_items" if int(self.options.floor_unlock_mode.value) == 1 else "start_with_all"

    def _per_floor_payment_checks(self) -> bool:
        return int(self.options.floor_payment_checks.value) == 1

    def _starting_symbol_mode_v141(self) -> str:
        try:
            value = int(getattr(self.options, "starting_symbol_mode").value)
        except Exception:
            value = 0
        return "starting_symbols" if value == 1 else "ap_checks"

    def _spin_ap_checks_mode(self) -> bool:
        """True means AP Check appears through symbol choices instead of replacing the start board.

        V141 removes the old automatic over-100 AP Check mode. The YAML option
        starting_symbol_mode now decides this directly.
        """
        return self._starting_symbol_mode_v141() == "starting_symbols"

    def _deathlink_enabled(self) -> bool:
        try:
            return int(getattr(self.options, "deathlink").value) == 1
        except Exception:
            return False

    def _deathlink_receive_chance(self) -> int:
        try:
            return max(0, min(100, int(getattr(self.options, "deathlink_receive_chance").value)))
        except Exception:
            return 100

    def _deathlink_receive_threshold(self) -> int:
        try:
            return max(1, min(20, int(getattr(self.options, "deathlink_receive_threshold").value)))
        except Exception:
            return 1

    def _deathlink_send_threshold(self) -> int:
        try:
            return max(1, min(20, int(getattr(self.options, "deathlink_send_threshold").value)))
        except Exception:
            return 1

    def _raspberry_pool_count(self) -> int:
        """Number of Raspberry items to add to the AP pool.

        This helper is used in generate_early, create_items, and slot_data.
        Keep it clamped here so old YAML/UT slot_data cannot exceed the option cap.
        """
        try:
            value = int(self.options.raspberry_pool.value)
        except Exception:
            value = 0
        return max(0, min(50, value))

    def _raspberry_required_count(self) -> int:
        """Number of Raspberry items needed for goal completion.

        A YAML value of 0 means require every Raspberry in the pool.
        """
        pool = int(getattr(self, "raspberry_pool_count", self._raspberry_pool_count()))
        if pool <= 0:
            return 0
        try:
            required = int(self.options.raspberry_required.value)
        except Exception:
            required = 0
        if required <= 0:
            required = pool
        return max(1, min(pool, min(50, required)))

    def _raspberry_enabled(self) -> bool:
        return self._raspberry_pool_count() > 0

    def _rare_very_rare_in_game_pool_enabled(self) -> bool:
        value = getattr(self.options, "rare_very_rare_in_game_pool", None)
        if value is None:
            return True
        return int(value.value) == 1

    def _item_randomizer_enabled(self) -> bool:
        return int(getattr(self.options, "item_randomizer").value) == 1

    def _essence_randomizer_enabled(self) -> bool:
        return int(getattr(self.options, "essence_randomizer").value) == 1

    def _progressive_ap_checks_enabled(self) -> bool:
        try:
            return int(getattr(self.options, "progressive_ap_checks").value) == 1
        except Exception:
            return True

    def _progressive_ap_checks_needed(self) -> int:
        if not self._progressive_ap_checks_enabled():
            return 0
        filler_count = max(0, int(self.options.extra_filler_checks.value))
        groups = (filler_count + 9) // 10
        return max(0, groups - 1)

    def _unlockable_chance_boost_enabled(self) -> bool:
        try:
            return int(getattr(self.options, "unlockable_chance_boost").value) == 1
        except Exception:
            return False

    def _unlockable_chance_weight(self) -> int:
        # Compatibility for the client/future old slot_data readers:
        # boost on behaves like the old maximum focus weight, off behaves vanilla.
        return 10 if self._unlockable_chance_boost_enabled() else 1

    def _unlockable_chance_boost_mode(self) -> str:
        try:
            value = int(getattr(self.options, "unlockable_chance_boost_mode").value)
        except Exception:
            value = 0
        return "category_and_rarity" if value == 1 else "category"

    def _rare_checks_enabled(self) -> bool:
        return int(getattr(self.options, "rare_checks").value) == 1

    def _very_rare_checks_enabled(self) -> bool:
        return int(getattr(self.options, "very_rare_checks").value) == 1

    def _disabled_rarity_first_get_locations(self) -> set[str]:
        """First-Get locations disabled by rarity options.

        These options only apply when bundles are off. With bundles on, First-Get
        checks are already disabled by bundle mode. Unlock items are not removed;
        this only stops those Rare/Very Rare gets from counting as checks.
        """
        disabled: set[str] = set()
        if not self._rare_checks_enabled():
            disabled.update(f"Send: {name}" for name in RARE_SYMBOLS)
            disabled.update(f"Send: {name}" for name in RARE_ITEMS)
            disabled.update(f"Send: {name}" for name in RARE_ESSENCES)
        if not self._very_rare_checks_enabled():
            disabled.update(f"Send: {name}" for name in VERY_RARE_SYMBOLS)
            disabled.update(f"Send: {name}" for name in VERY_RARE_ITEMS)
            disabled.update(f"Send: {name}" for name in VERY_RARE_ESSENCES)

        # These non-rare/exception checks are normal reachable LBAL content and should remain
        # available even when rarity-trimming options are enabled. V135: Diamond is not
        # exempt here; it is Very Rare and should respect very_rare_checks.
        # Dud and Missing are not actually selectable/grabbable symbols, so they
        # must never become First Get checks. They are also removed from SYMBOLS
        # in Items.py, but keep this defensive cleanup for old slot data/UT.
        disabled.difference_update({
            "Send: Wealthy Capsule",
            "Send: The Tortoise and the Hare",
            "Send: Big Symbol Bomb",
            "Send: Quantum Symbol Bomb",
            # Extra user-requested checks that should stay available even when
            # rare/very-rare trimming is enabled.
            "Send: Big Symbol Bomb Essence",
            "Send: Black Suits Essence",
            "Send: Fish Tank Essence",
            "Send: Kyle the Kernite",
            "Send: Kyle the Kernite Essence",
            "Send: Small Symbol Bomb Essence",
            "Send: The Tortoise and the Hare Essence",
            "Send: Very Big Symbol Bomb Essence",
        })
        disabled.update({
            "Send: Dud",
            "Send: Missing",
        })
        return disabled

    def _enabled_location_names(self) -> list[str]:
        if not hasattr(self, "goal_floors"):
            self.goal_floors = self._choose_goal_floors()
        if not hasattr(self, "goal_floors_required"):
            self.goal_floors_required = self._choose_goal_floors_required()

        filler_count = int(self.options.extra_filler_checks.value)
        disabled_rarity_first_get = set() if self._bundles_enabled() else self._disabled_rarity_first_get_locations()
        enabled = []
        for name in location_table:
            if name in FILLER_CHECK_LOCATIONS:
                index = FILLER_CHECK_LOCATIONS.index(name)
                if index >= filler_count:
                    continue
            if name in PAYMENT_LOCATIONS and self._per_floor_payment_checks():
                continue
            sent_name = name.removeprefix("Send: ") if name.startswith("Send: ") else None
            # Item and essence randomizer toggles decide whether their Send
            # locations exist. When off, that content is vanilla and not AP.
            if sent_name in NORMAL_ITEMS and not self._item_randomizer_enabled():
                continue
            if sent_name in ESSENCES and not self._essence_randomizer_enabled():
                continue
            # If bundles are enabled, normal First-Get checks are disabled.
            # The bundle AP item is the unlock; AP Checks, Payments, and Floor Goals remain as checks.
            if self._bundles_enabled() and name.startswith("Send: "):
                continue
            if name in disabled_rarity_first_get:
                continue
            if name in FLOOR_PAYMENT_LOCATIONS:
                if not self._per_floor_payment_checks():
                    continue
                parts = name.split()
                floor = int(parts[1])
                if floor not in self.goal_floors:
                    continue
            if name in FLOOR_GOAL_LOCATIONS and name not in {floor_goal_location_name(floor) for floor in self.goal_floors}:
                continue
            enabled.append(name)
        return enabled
