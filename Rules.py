from __future__ import annotations

from worlds.generic.Rules import set_rule, add_item_rule

from .Items import SYMBOLS, NORMAL_ITEMS, ESSENCES, RASPBERRY_ITEM_NAME, FILLER_ITEMS, PROGRESSIVE_AP_CHECKS_ITEM_NAME
from .Locations import (
    FILLER_CHECK_LOCATIONS,
    SPHERE_ONE_CHECKS,
    floor_goal_event_name,
    FLOOR_PAYMENT_LOCATIONS,
    floor_goal_location_name,
    floor_goal_requirement,
    payment_event_name,
)


def has_any(world, state, names: list[str]) -> bool:
    return any(world.has_unlock_access(state, name) for name in names)


def has_all(world, state, names: list[str]) -> bool:
    return all(world.has_unlock_access(state, name) for name in names)


def has_count(world, state, names: list[str], count: int) -> bool:
    return sum(1 for name in names if world.has_unlock_access(state, name)) >= count


def has_any_combo(world, state, combos: list[list[str]]) -> bool:
    return any(has_all(world, state, combo) for combo in combos)


EARLY_SYMBOL_UNLOCKS = [
    "Unlock: Cherry",
    "Unlock: Coin",
    "Unlock: Cat",
    "Unlock: Dog",
    "Unlock: Bee",
    "Unlock: Flower",
    "Unlock: Mouse",
    "Unlock: Cheese",
    "Unlock: Milk",
    "Unlock: Dwarf",
    "Unlock: Beer",
    "Unlock: Wine",
    "Unlock: Toddler",
    "Unlock: Candy",
    "Unlock: Banana",
    "Unlock: Monkey",
    "Unlock: Key",
    "Unlock: Lockbox",
]

EARLY_ITEM_UNLOCKS = [
    "Unlock: Pizza the Cat",
    "Unlock: Lucky Cat",
    "Unlock: Pool Ball",
    "Unlock: Rain Cloud",
    "Unlock: Lunchbox",
    "Unlock: Lockpick",
    "Unlock: Mining Pick",
    "Unlock: Ricky the Banana",
]

MIDGAME_SYMBOL_UNLOCKS = [
    "Unlock: Bear",
    "Unlock: Coconut",
    "Unlock: Coconut Half",
    "Unlock: Rabbit",
    "Unlock: Rabbit Fluff",
    "Unlock: Wolf",
    "Unlock: Safe",
    "Unlock: Thief",
    "Unlock: Hooligan",
    "Unlock: Target",
    "Unlock: Clubs",
    "Unlock: Diamonds",
    "Unlock: Hearts",
    "Unlock: Spades",
    "Unlock: Rain",
    "Unlock: Big Ore",
    "Unlock: Mine",
    "Unlock: Honey",
]

MIDGAME_ITEM_UNLOCKS = [
    "Unlock: Nori the Rabbit",
    "Unlock: Maxwell the Bear",
    "Unlock: Ninja and Mouse",
    "Unlock: Fruit Basket",
    "Unlock: Cleaning Rag",
    "Unlock: Rusty Gear",
    "Unlock: Conveyor Belt",
    "Unlock: Fertilizer",
    "Unlock: Watering Can",
]

LATEGAME_SYMBOL_UNLOCKS = [
    "Unlock: Pirate",
    "Unlock: Geologist",
    "Unlock: Mrs. Fruit",
    "Unlock: Diver",
    "Unlock: Farmer",
    "Unlock: Sun",
    "Unlock: Moon",
    "Unlock: Beastmaster",
    "Unlock: Joker",
    "Unlock: Card Shark",
    "Unlock: Eldritch Creature",
    "Unlock: Diamond",
    "Unlock: Wildcard",
    "Unlock: Dame",
    "Unlock: King Midas",
    "Unlock: Magic Key",
    "Unlock: Treasure Chest",
]

LATEGAME_ITEM_UNLOCKS = [
    "Unlock: Protractor",
    "Unlock: Telescope",
    "Unlock: Copycat",
    "Unlock: Golden Carrot",
    "Unlock: Mobius Strip",
    "Unlock: Recycling",
    "Unlock: Very Big Symbol Bomb",
    "Unlock: Quiver",
]

EARLY_COMBOS = [
    ["Unlock: Mouse", "Unlock: Cheese"],
    ["Unlock: Dwarf", "Unlock: Beer"],
    ["Unlock: Dwarf", "Unlock: Wine"],
    ["Unlock: Toddler", "Unlock: Candy"],
    ["Unlock: Cat", "Unlock: Pizza the Cat"],
    ["Unlock: Cat", "Unlock: Milk"],
    ["Unlock: Monkey", "Unlock: Banana"],
    ["Unlock: Key", "Unlock: Lockbox"],
]

MIDGAME_COMBOS = [
    ["Unlock: Bear", "Unlock: Honey"],
    ["Unlock: Thief", "Unlock: Hooligan"],
    ["Unlock: Safe", "Unlock: Lockpick"],
    ["Unlock: Clubs", "Unlock: Diamonds", "Unlock: Hearts", "Unlock: Spades"],
    ["Unlock: Rabbit", "Unlock: Rabbit Fluff"],
    ["Unlock: Rabbit", "Unlock: Nori the Rabbit"],
    ["Unlock: Big Ore", "Unlock: Mining Pick"],
    ["Unlock: Flower", "Unlock: Bee", "Unlock: Rain"],
    ["Unlock: Coconut", "Unlock: Coconut Half"],
]

LATEGAME_COMBOS = [
    ["Unlock: Geologist", "Unlock: Ore"],
    ["Unlock: Geologist", "Unlock: Big Ore"],
    ["Unlock: Mrs. Fruit", "Unlock: Apple"],
    ["Unlock: Diver", "Unlock: Pearl"],
    ["Unlock: Diver", "Unlock: Treasure Chest"],
    ["Unlock: Farmer", "Unlock: Seed"],
    ["Unlock: Sun", "Unlock: Flower"],
    ["Unlock: Sun", "Unlock: Rain", "Unlock: Flower"],
    ["Unlock: Joker", "Unlock: Card Shark"],
    ["Unlock: Pirate", "Unlock: Treasure Chest"],
    ["Unlock: Pirate", "Unlock: Anchor"],
    ["Unlock: Eldritch Creature", "Unlock: Cultist"],
    ["Unlock: Eldritch Creature", "Unlock: Hex of Midas"],
    ["Unlock: Dame", "Unlock: Diamond"],
    ["Unlock: Magic Key", "Unlock: Treasure Chest"],
]


def can_clear_payment(world, state, payment: int) -> bool:
    """Payment logic tied to Progressive AP Checks.

    Progressive AP Checks open AP Check blocks of 10. Payments wait for those
    progressive unlocks first: Payment 1 needs the first Progressive AP Checks
    item, Payment 2 needs the second, and so on. Once every Progressive AP
    Checks item needed by the seed has been collected, all payments become
    logically available. If the option is disabled, payments fall back to the
    older sequential payment chain.
    """
    progressive_enabled = bool(getattr(world, "_progressive_ap_checks_enabled", lambda: False)())
    progressive_needed = int(getattr(world, "_progressive_ap_checks_needed", lambda: 0)() or 0)
    if progressive_enabled and progressive_needed > 0:
        required_progressive = min(int(payment), progressive_needed)
        return state.has(PROGRESSIVE_AP_CHECKS_ITEM_NAME, world.player, required_progressive)

    if payment == 1:
        return True
    return state.has(payment_event_name(payment - 1), world.player)


def floor_available_for_logic(world, state, floor: int) -> bool:
    """A per-floor payment check cannot enter logic until that AP floor is unlocked.

    In start_with_all mode every selected floor is open. In unlock_through_items
    mode, the first selected floor is open at start and later selected floors
    require their matching Unlock Floor X item.
    """
    floor = int(floor)
    goal_floors = [int(f) for f in getattr(world, "goal_floors", []) or [floor]]
    first_floor = goal_floors[0] if goal_floors else floor
    floor_mode = getattr(world, "_floor_unlock_mode", lambda: "start_with_all")()
    if floor == first_floor:
        return True
    if floor_mode != "unlock_through_items":
        return True
    return state.has(f"Unlock Floor {floor}", world.player)


def can_clear_floor_payment(world, state, floor: int, payment: int) -> bool:
    """Per-floor version of can_clear_payment.

    Each Floor X Payment Y uses the same payment logic as the shared Payment Y,
    but also requires Floor X to be unlocked first. If Progressive AP Checks are
    disabled, each floor keeps its own local payment chain, so Floor 5 Payment 2
    depends on Floor 5 Payment 1 rather than another floor's Payment 1.
    """
    floor = int(floor)
    payment = int(payment)

    if not floor_available_for_logic(world, state, floor):
        return False

    progressive_enabled = bool(getattr(world, "_progressive_ap_checks_enabled", lambda: False)())
    progressive_needed = int(getattr(world, "_progressive_ap_checks_needed", lambda: 0)() or 0)
    if progressive_enabled and progressive_needed > 0:
        return can_clear_payment(world, state, payment)

    if payment <= 1:
        return True

    previous_name = f"Floor {floor} Payment {payment - 1}"
    try:
        return state.can_reach(previous_name, "Location", world.player)
    except Exception:
        return False


def required_payment_for_floor(floor: int) -> int:
    # Payment 13 is disabled because it is unstable in-game.
    return 12


def _is_universal_tracker_generation(world) -> bool:
    return bool(getattr(world.multiworld, "generation_is_fake", False))


def _ut_location_checked(world, state, location_name: str) -> bool:
    """Best-effort checked-location test for Universal Tracker.

    Normal Archipelago generation cannot use checked locations in logic, but UT
    has a live tracker state. Different UT/AP versions store checked locations
    slightly differently, so this checks the common forms and safely falls back
    to False instead of opening every payment sphere immediately.
    """
    try:
        location = world.multiworld.get_location(location_name, world.player)
    except Exception:
        location = None

    def _checked_contains(checked) -> bool:
        if checked is None:
            return False
        candidates = {location_name}
        if location is not None:
            candidates.add(location)
            candidates.add(getattr(location, "name", None))
            candidates.add(getattr(location, "address", None))
            candidates.add((world.player, getattr(location, "address", None)))
            candidates.add((world.player, getattr(location, "name", None)))
            candidates.add((getattr(location, "address", None), world.player))
            candidates.add((getattr(location, "name", None), world.player))
        candidates.discard(None)

        try:
            if isinstance(checked, dict):
                for key in (world.player, str(world.player), getattr(world, "player_name", None), "locations_checked", "checked_locations"):
                    value = checked.get(key) if key in checked else None
                    if _checked_contains(value):
                        return True
                for value in checked.values():
                    if _checked_contains(value):
                        return True
                return False

            if isinstance(checked, (list, set, tuple, frozenset)):
                for candidate in candidates:
                    if candidate in checked:
                        return True
                return False

            return checked in candidates
        except Exception:
            return False

    for attr in (
        "locations_checked", "checked_locations", "checked_location_names",
        "location_checks", "location_checked", "checked",
    ):
        if _checked_contains(getattr(state, attr, None)):
            return True

    for attr in (
        "locations_checked", "checked_locations", "checked_location_names",
        "location_checks", "location_checked", "checked",
    ):
        if _checked_contains(getattr(world.multiworld, attr, None)):
            return True

    try:
        prog = getattr(state, "prog_items", {})
        if (world.player, f"@Checked Location: {location_name}") in prog:
            return True
    except Exception:
        pass

    return False


def _payment_cleared_for_logic(world, state, payment: int, floor: int | None = None) -> bool:
    if getattr(world.options, "floor_payment_checks", None) and int(world.options.floor_payment_checks.value) == 1:
        if floor is not None:
            return _ut_location_checked(world, state, f"Floor {int(floor)} Payment {int(payment)}")
        return any(
            _ut_location_checked(world, state, f"Floor {int(f)} Payment {int(payment)}")
            for f in getattr(world, "goal_floors", [])
        )
    if hasattr(world, "get_location"):
        return _ut_location_checked(world, state, f"Payment {int(payment)}")
    return state.has(payment_event_name(payment), world.player)



def set_rules(world) -> None:
    """
    Logic/spheres for Luck be a Landlord.

    Sphere 1 starts with AP Check 1 through AP Check 10.

    With Progressive AP Checks enabled, Payment 1 requires the first Progressive
    AP Checks item, Payment 2 requires the second, and after all Progressive AP
    Checks items are owned the rest of the payments are all in logic. AP Checks
    are split into groups of 10 by Progressive AP Checks.
    First Get checks only become logically reachable after AP has sent the matching unlock item.
    """

    enabled_locations = set(world._enabled_location_names())
    spin_ap_checks_mode = bool(getattr(world, "_spin_ap_checks_mode", lambda: False)())

    # Progressive AP Checks handle AP Check spheres directly. Do not open Send:
    # locations with generation-only fallback logic, because external sphere
    # trackers then show every Send check as sphere 1.
    def generation_send_fallback(state, location_name: str) -> bool:
        return False

    def keep_fillers_off_progression_send_locations(location_name: str) -> None:
        """No-op kept for compatibility with older patch points.

        Unlock items now stay progression, so restrictive fill will place them
        before filler naturally. Blocking filler from every Send: location made
        reduced-check seeds run out of legal filler spots after unlocks used the
        AP Check/payment locations.
        """
        return None

    # Payment checks are real AP locations with normal randomized items.
    # Separate hidden event locations grant "Payment X Cleared" for sphere logic.
    # V28: per-floor mode disables shared "Payment X" locations, so only call
    # world.get_location("Payment X") if that location is actually enabled.
    per_floor_payments = (
        getattr(world.options, "floor_payment_checks", None)
        and int(world.options.floor_payment_checks.value) == 1
    )

    for payment in range(1, 13):
        payment_rule = lambda state, payment=payment: can_clear_payment(world, state, payment)

        shared_payment_name = f"Payment {payment}"
        if shared_payment_name in enabled_locations:
            set_rule(world.get_location(shared_payment_name), payment_rule)

        event_location = world.get_location(payment_event_name(payment))
        event_location.place_locked_item(world.create_event(payment_event_name(payment)))
        if per_floor_payments:
            set_rule(event_location, lambda state, payment=payment: any(can_clear_floor_payment(world, state, floor, payment) for floor in getattr(world, "goal_floors", [])))
        else:
            set_rule(event_location, payment_rule)

    # Optional per-floor payment checks. These are normal AP checks with the same payment logic,
    # separated by selected floor number for multi-floor seeds.
    if per_floor_payments:
        for floor in world.goal_floors:
            for payment in range(1, 13):
                name = f"Floor {floor} Payment {payment}"
                if name in enabled_locations:
                    set_rule(world.get_location(name), lambda state, payment=payment, floor=floor: can_clear_floor_payment(world, state, floor, payment))

    # Split AP Check locations into groups of 10.
    # AP Check 1-10 are open at start.
    # AP Check 11-20 require 1 Progressive AP Checks item, 21-30 require 2, etc.
    # The first AP Check in each block is locked to the next Progressive AP Checks item.
    #
    # Important: only assign rules to locations that are actually enabled for
    # this player's options. Older YAMLs may still set extra_filler_checks: 30,
    # while this APWorld supports up to 100. Calling get_location("AP Check 31")
    # when that option only enabled 30 checks causes generation to crash.
    for index, check_name in enumerate(FILLER_CHECK_LOCATIONS, start=1):
        if check_name not in enabled_locations:
            continue
        required_progressive = (index - 1) // 10
        if required_progressive <= 0:
            continue
        if bool(getattr(world, "_progressive_ap_checks_enabled", lambda: True)()):
            set_rule(
                world.get_location(check_name),
                lambda state, required_progressive=required_progressive: state.has(
                    PROGRESSIVE_AP_CHECKS_ITEM_NAME, world.player, required_progressive
                ),
            )
        else:
            required_payment = min(12, required_progressive)
            set_rule(
                world.get_location(check_name),
                lambda state, required_payment=required_payment: _payment_cleared_for_logic(
                    world, state, required_payment
                ),
            )

    # First-Get locations are only checks when item bundles are OFF.
    # When bundles are ON, the bundle AP item itself unlocks its contents and these checks are disabled.
    # First-Get checks are gated by their matching AP unlock during real
    # generation and tracker use. This makes spoiler/sphere tracker output match
    # the client Tracker instead of putting every Send: location in sphere 1.
    if not world._bundles_enabled():
        for symbol in SYMBOLS:
            name = f"Send: {symbol}"
            if name in enabled_locations:
                # Use the real unlock gate during generation too. Earlier builds
                # made these True in low-filler/spin-check mode to make filling
                # easier, but that causes external sphere trackers to show every
                # Send: location in sphere 1. AP's normal fill can still place the
                # unlocks in AP Checks/payments first, then unlock these checks in
                # later spheres.
                set_rule(
                    world.get_location(name),
                    lambda state, symbol=symbol, name=name: (
                        world.has_unlock_access(
                            state,
                            "Unlock: Matryoshka Doll" if symbol in {"Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5"} else f"Unlock: {symbol}"
                        )
                        or generation_send_fallback(state, name)
                    ),
                )
                keep_fillers_off_progression_send_locations(name)

        for item in NORMAL_ITEMS:
            name = f"Send: {item}"
            if name in enabled_locations:
                def item_send_rule(state, item=item, name=name):
                    if not world.has_unlock_access(state, f"Unlock: {item}"):
                        return generation_send_fallback(state, name)
                    # Suits items need at least one matching suit symbol unlocked/sent first.
                    # This prevents Black/Red Suits from appearing as obtainable before
                    # the player has a card suit that can actually make them useful.
                    if item == "Red Suits":
                        return (
                            world.has_unlock_access(state, "Unlock: Diamonds")
                            or world.has_unlock_access(state, "Unlock: Hearts")
                            or state.can_reach("Send: Diamonds", "Location", world.player)
                            or state.can_reach("Send: Hearts", "Location", world.player)
                            or generation_send_fallback(state, name)
                        )
                    if item == "Black Suits":
                        return (
                            world.has_unlock_access(state, "Unlock: Spades")
                            or world.has_unlock_access(state, "Unlock: Clubs")
                            or state.can_reach("Send: Spades", "Location", world.player)
                            or state.can_reach("Send: Clubs", "Location", world.player)
                            or generation_send_fallback(state, name)
                        )
                    return True

                set_rule(world.get_location(name), item_send_rule)
                keep_fillers_off_progression_send_locations(name)

        if world._essence_randomizer_enabled():
            for essence in ESSENCES:
                name = f"Send: {essence}"
                if name in enabled_locations:
                    set_rule(
                        world.get_location(name),
                        lambda state, essence=essence, name=name: (
                            world.has_unlock_access(state, f"Unlock: {essence}")
                            or generation_send_fallback(state, name)
                        ),
                    )
                    keep_fillers_off_progression_send_locations(name)


    # Floor goal checks are real AP locations with normal randomized items.
    # Separate hidden victory event locations drive the actual completion condition.
    for floor in world.goal_floors:
        required_payment = required_payment_for_floor(floor)
        def goal_rule(state, required_payment=required_payment, floor=floor):
            # Floor clear should only show when the floor is actually available.
            # For selected multi-floor seeds, the first selected floor is open;
            # every other selected floor needs its Unlock Floor item before the
            # clear can appear in trackers. This also keeps Universal Tracker
            # from showing Clear Floor 10/20 before those floors are owned.
            floor_ok = floor_available_for_logic(world, state, floor)
            if getattr(world.options, "floor_payment_checks", None) and int(world.options.floor_payment_checks.value) == 1:
                return floor_ok and can_clear_floor_payment(world, state, floor, required_payment)
            return floor_ok and _payment_cleared_for_logic(world, state, required_payment, floor)

        set_rule(world.get_location(floor_goal_location_name(floor)), goal_rule)

        event_location = world.get_location(floor_goal_event_name(floor))
        event_location.place_locked_item(world.create_event(floor_goal_event_name(floor)))
        set_rule(event_location, goal_rule)

    required_floor_count = max(1, min(
        int(getattr(world, "goal_floors_required", len(world.goal_floors))),
        len(world.goal_floors),
    ))
    raspberry_required = int(getattr(world, "raspberry_required_count", 0) or 0)

    def completion_rule(state):
        # The server-side beatability check should prove the seed can reach the
        # end of the rent ladder plus Raspberry goal. The real client still only
        # sends CLIENT_GOAL after the selected floor clear checks are sent, and
        # /goal is guarded by all real checks plus Raspberry.
        #
        # Requiring the hidden Victory Floor event here can make Archipelago
        # declare otherwise-valid reduced-AP-check seeds unbeatable, because
        # those events are only internal tracker logic while floor clears are
        # sent by the LBAL client from the game log.
        if not state.has(payment_event_name(12), world.player):
            return False
        if raspberry_required > 0:
            return state.has(RASPBERRY_ITEM_NAME, world.player, raspberry_required)
        return True

    world.multiworld.completion_condition[world.player] = completion_rule
