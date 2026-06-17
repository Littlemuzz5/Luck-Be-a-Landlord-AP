from __future__ import annotations

from typing import Dict, List, NamedTuple
from BaseClasses import Location
from .Items import SYMBOLS, NORMAL_ITEMS, ESSENCES


class LuckLocation(Location):
    game: str = "Luck be a Landlord"


class LocationData(NamedTuple):
    code: int | None
    category: str


LOCATION_BASE_ID = 777780000
DEFAULT_FILLER_CHECKS = 200

FIRST_GET_SYMBOL_LOCATIONS: List[str] = [f"Send: {name}" for name in SYMBOLS]
FIRST_GET_ITEM_LOCATIONS: List[str] = [f"Send: {name}" for name in NORMAL_ITEMS]
FIRST_GET_ESSENCE_LOCATIONS: List[str] = [f"Send: {name}" for name in ESSENCES]
FILLER_CHECK_LOCATIONS: List[str] = [f"AP Check {i}" for i in range(1, DEFAULT_FILLER_CHECKS + 1)]
PAYMENT_LOCATIONS: List[str] = [f"Payment {i}" for i in range(1, 13)]
FLOOR_PAYMENT_LOCATIONS: List[str] = [f"Floor {floor} Payment {payment}" for floor in range(1, 21) for payment in range(1, 13)]
SPHERE_ONE_CHECKS: List[str] = FILLER_CHECK_LOCATIONS[:10]
FLOOR_GOAL_LOCATIONS: List[str] = [f"Clear Floor {i} Goal" for i in range(1, 21)]

LOCATION_NAMES: List[str] = (
    PAYMENT_LOCATIONS
    + FLOOR_PAYMENT_LOCATIONS
    + FIRST_GET_SYMBOL_LOCATIONS
    + FIRST_GET_ITEM_LOCATIONS
    + FIRST_GET_ESSENCE_LOCATIONS
    + FILLER_CHECK_LOCATIONS
    + FLOOR_GOAL_LOCATIONS
)

location_table: Dict[str, LocationData] = {}
for index, location_name in enumerate(LOCATION_NAMES):
    if location_name in FLOOR_GOAL_LOCATIONS:
        category = "Floor Goals"
    else:
        category = "Check"
    location_table[location_name] = LocationData(LOCATION_BASE_ID + index, category)

location_name_groups = {
    "Send Symbols": frozenset(FIRST_GET_SYMBOL_LOCATIONS),
    "Send Items": frozenset(FIRST_GET_ITEM_LOCATIONS),
    "Send Essences": frozenset(FIRST_GET_ESSENCE_LOCATIONS),
    "AP Checks": frozenset(FILLER_CHECK_LOCATIONS),
    "Payments": frozenset(PAYMENT_LOCATIONS),
    "Floor Payments": frozenset(FLOOR_PAYMENT_LOCATIONS),
    "Sphere One": frozenset(SPHERE_ONE_CHECKS),
    "Floor Goals": frozenset(FLOOR_GOAL_LOCATIONS),
}


def floor_goal_location_name(floor: int) -> str:
    return f"Clear Floor {floor} Goal"


def floor_goal_event_name(floor: int) -> str:
    return f"Victory Floor {floor}"


def floor_goal_requirement(floor: int) -> str:
    # Floor 1-20: beat/payment 12. Payment 13 is disabled because it is unstable in-game.
    return "beat_payment_12"


def payment_event_name(payment: int) -> str:
    return f"Payment {payment} Cleared"
