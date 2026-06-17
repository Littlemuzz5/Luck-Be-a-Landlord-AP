from __future__ import annotations

from typing import Dict, List, NamedTuple
from .EasyContent import EASY_SYMBOL_NAMES, EASY_ITEM_NAMES, EASY_ESSENCE_NAMES
from BaseClasses import Item, ItemClassification


class LuckItem(Item):
    game: str = "Luck be a Landlord"


class ItemData(NamedTuple):
    code: int | None
    classification: ItemClassification
    category: str


ITEM_BASE_ID = 777770000

SYMBOLS: List[str] = [
    "Anchor", "Banana", "Banana Peel", "Bee", "Beer", "Bounty Hunter", "Bubble", "Candy", "Cat",
    "Cheese", "Cherry", "Coal", "Coin", "Crab", "Crow", "Cultist", "Dog", "Dwarf", "Egg", "Flower",
    "Gambler", "Goldfish", "Goose", "Key", "Light Bulb", "Lockbox", "Magpie", "Milk", "Miner", "Monkey",
    "Mouse", "Ore", "Owl", "Oyster", "Pearl", "Present", "Seed", "Shiny Pebble", "Snail", "Three-Sided Die",
    "Toddler", "Turtle", "Urn",
    "Bar of Soap", "Bear", "Big Ore", "Big Urn", "Billionaire", "Bronze Arrow", "Buffing Capsule",
    "Chemical Seven", "Chick", "Clubs", "Coconut", "Coconut Half", "Diamonds", "Essence Capsule",
    "Five-Sided Die", "Golem", "Hearts", "Hex of Destruction", "Hex of Draining", "Hex of Emptiness",
    "Hex of Hoarding", "Hex of Midas", "Hex of Tedium", "Hex of Thievery", "Hooligan", "Hustling Capsule",
    "Jellyfish", "Lucky Capsule", "Matryoshka Doll", "Ninja", "Orange", "Peach", "Piñata",
    "Pufferfish", "Rabbit", "Rabbit Fluff", "Rain", "Removal Capsule", "Reroll Capsule", "Safe", "Sand Dollar",
    "Sapphire", "Sloth", "Spades", "Target", "Tedium Capsule", "Thief", "Time Capsule", "Void Creature",
    "Void Fruit", "Void Stone", "Wealthy Capsule", "Wine", "Wolf",
    "Amethyst", "Apple", "Bartender", "Beastmaster", "Beehive", "Card Shark", "Chef", "Chicken", "Comedian",
    "Cow", "Dame", "Diver", "Dove", "Emerald", "Farmer", "Frozen Fossil", "General Zaroff", "Geologist",
    "Golden Egg", "Honey", "Joker", "King Midas", "Magic Key", "Martini", "Mine", "Moon", "Mrs. Fruit",
    "Omelette", "Pear", "Robin Hood", "Ruby", "Silver Arrow", "Spirit", "Strawberry", "Sun", "Tomb",
    "Treasure Chest", "Witch",
    "Diamond", "Eldritch Creature", "Golden Arrow", "Highlander", "Mega Chest", "Midas Bomb", "Pirate",
    "Watermelon", "Wildcard",
    "Empty", "Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5",
]

NORMAL_ITEMS: List[str] = [
    "5th Ace", "Adoption Papers", "Birdhouse", "Black Pepper", "Black Suits", "Blue Pepper", "Brown Pepper",
    "Checkered Flag", "Cyan Pepper", "Dwarven Anvil", "Egg Carton", "Fish Tank", "Frying Pan", "Grave Robber",
    "Gray Pepper", "Green Pepper", "Guillotine", "Happy Hour", "Jack-o'-lantern", "Kyle the Kernite",
    "Lime Pepper", "Lockpick", "Lucky Cat", "Lucky Seven", "Lunchbox", "Maxwell the Bear", "Mining Pick",
    "Ninja and Mouse", "Nori the Rabbit", "Oswald the Monkey", "Pink Pepper", "Pizza the Cat", "Pool Ball",
    "Purple Pepper", "Quigley the Wolf", "Rain Cloud", "Red Pepper", "Red Suits", "Reroll", "Ricky the Banana",
    "Shedding Season", "Small Symbol Bomb", "Swear Jar", "Tax Evasion", "The Tortoise and the Hare", "Treasure Map",
    "Wanted Poster", "Watering Can", "White Pepper", "Yellow Pepper",
    "Barrel of Dwarves", "Big Symbol Bomb", "Black Cat", "Cardboard Box", "Cleaning Rag", "Coin on a String",
    "Comfy Pillow", "Compost Heap", "Conveyor Belt", "Cursed Katana", "Dark Humor", "Fertilizer", "Flush",
    "Fruit Basket", "Goldilocks", "Horseshoe", "Lefty the Rabbit", "Lemon", "Lint Roller", "Looting Glove",
    "Piggy Bank", "Quantum Symbol Bomb", "Ritual Candle", "Rusty Gear", "Shattered Mirror", "Shrine", "Time Machine",
    "Triple Coins", "X-ray Machine", "Zaroff's Contract",
    "Anthropology Degree", "Booster Pack", "Bowling Ball", "Capsule Machine", "Chicken Coop", "Chili Powder",
    "Clear Sky", "Coffee", "Devil's Deal", "Dishwasher", "Holy Water", "Lucky Carrot",
    "Lucky Dice", "Oil Can", "Protractor", "Quiver", "Sunglasses", "Swapping Device", "Undertaker",
    "Very Big Symbol Bomb", "Void Party", "Void Portal",
    "Ancient Lizard Blade", "Copycat", "Credit Card", "Four-leaf clover", "Frozen Pizza", "Golden Carrot",
    "Mobius Strip", "Popsicle", "Recycling", "Telescope",
]

ESSENCES: List[str] = [
    '5th Ace Essence', 'Adoption Papers Essence', 'Birdhouse Essence', 'Black Pepper Essence', 'Black Suits Essence',
    'Blue Pepper Essence', 'Brown Pepper Essence', 'Checkered Flag Essence', 'Cyan Pepper Essence',
    'Dwarven Anvil Essence', 'Egg Carton Essence', 'Fish Tank Essence', 'Frying Pan Essence', 'Grave Robber Essence',
    'Gray Pepper Essence', 'Green Pepper Essence', 'Guillotine Essence', 'Happy Hour Essence',
    "Jack-o'-lantern Essence", 'Kyle the Kernite Essence', 'Lime Pepper Essence', 'Lockpick Essence',
    'Lucky Cat Essence', 'Lucky Seven Essence', 'Lunchbox Essence', 'Maxwell the Bear Essence', 'Mining Pick Essence',
    'Ninja and Mouse Essence', 'Nori the Rabbit Essence', 'Oswald the Monkey Essence', 'Pink Pepper Essence',
    'Pizza the Cat Essence', 'Pool Ball Essence', 'Purple Pepper Essence', 'Quigley the Wolf Essence',
    'Rain Cloud Essence', 'Red Pepper Essence', 'Red Suits Essence', 'Reroll Essence', 'Ricky the Banana Essence',
    'Shedding Season Essence', 'Small Symbol Bomb Essence', 'Swear Jar Essence', 'Tax Evasion Essence',
    'The Tortoise and the Hare Essence', 'Treasure Map Essence', 'Wanted Poster Essence', 'Watering Can Essence',
    'White Pepper Essence', 'Yellow Pepper Essence', 'Barrel of Dwarves Essence', 'Big Symbol Bomb Essence',
    'Black Cat Essence', 'Cardboard Box Essence', 'Cleaning Rag Essence', 'Coin on a String Essence',
    'Comfy Pillow Essence', 'Compost Heap Essence', 'Conveyor Belt Essence', 'Cursed Katana Essence',
    'Dark Humor Essence', 'Fertilizer Essence', 'Flush Essence', 'Fruit Basket Essence', 'Goldilocks Essence',
    'Horseshoe Essence', 'Lefty the Rabbit Essence', 'Lemon Essence', 'Lint Roller Essence', 'Looting Glove Essence',
    'Piggy Bank Essence', 'Quantum Symbol Bomb Essence', 'Ritual Candle Essence', 'Rusty Gear Essence',
    'Shattered Mirror Essence', 'Shrine Essence', 'Time Machine Essence', 'Triple Coins Essence',
    'X-ray Machine Essence', "Zaroff's Contract Essence", 'Anthropology Degree Essence', 'Booster Pack Essence',
    'Bowling Ball Essence', 'Capsule Machine Essence', 'Chicken Coop Essence', 'Chili Powder Essence',
    'Clear Sky Essence', 'Coffee Essence', "Devil's Deal Essence", 'Dishwasher Essence', 'Holy Water Essence',
    'Lucky Carrot Essence', 'Lucky Dice Essence', 'Oil Can Essence', 'Protractor Essence',
    'Quiver Essence', 'Sunglasses Essence', 'Swapping Device Essence', 'Undertaker Essence',
    'Very Big Symbol Bomb Essence', 'Void Party Essence', 'Void Portal Essence', 'Ancient Lizard Blade Essence',
    'Copycat Essence', 'Credit Card Essence', 'Four-leaf clover Essence', 'Frozen Pizza Essence',
    'Golden Carrot Essence', 'Mobius Strip Essence', 'Popsicle Essence', 'Recycling Essence', 'Telescope Essence',
]


# V21 easy content support: built-in content packs inside the .apworld can add
# simple symbols/items/essences without players installing a separate LBAL mod.
SYMBOLS.extend([name for name in EASY_SYMBOL_NAMES if name not in SYMBOLS])
NORMAL_ITEMS.extend([name for name in EASY_ITEM_NAMES if name not in NORMAL_ITEMS])
ESSENCES.extend([name for name in EASY_ESSENCE_NAMES if name not in ESSENCES])


def _list_between(values: List[str], first: str, last: str) -> List[str]:
    """Inclusive slice helper used to keep LBAL rarity groups in one place."""
    start = values.index(first)
    end = values.index(last)
    return values[start:end + 1]


# Rarity groups used by YAML options that disable First-Get checks.
# These do not remove the unlock items themselves; they only remove the matching
# "First Get ..." locations when bundles are off.
RARE_SYMBOLS: List[str] = _list_between(SYMBOLS, "Amethyst", "Witch")
VERY_RARE_SYMBOLS: List[str] = _list_between(SYMBOLS, "Diamond", "Wildcard")
RARE_ITEMS: List[str] = _list_between(NORMAL_ITEMS, "Anthropology Degree", "Void Portal")
VERY_RARE_ITEMS: List[str] = _list_between(NORMAL_ITEMS, "Ancient Lizard Blade", "Telescope")
RARE_ESSENCES: List[str] = _list_between(ESSENCES, "Anthropology Degree Essence", "Void Portal Essence")
VERY_RARE_ESSENCES: List[str] = _list_between(ESSENCES, "Ancient Lizard Blade Essence", "Telescope Essence")

FILLER_ITEM_NAME = "Progressive Filler"
FILLER_ITEMS: List[str] = ["Strawberry", "Progressive Filler", "Progressive Nothing"]
RASPBERRY_ITEM_NAME = "Raspberry"
PROGRESSIVE_AP_CHECKS_ITEM_NAME = "Progressive AP Checks"
BUNDLE_ITEM_PREFIX = "Unlock Bundle"

TRAP_ITEMS: List[str] = [
    "Trap: Half Money",
    "Trap: Force Payment",
    "Trap: Add Dud Symbol",
]

BUFF_ITEMS: List[str] = [
    "Buff: Start With a Destroy Token",
    "Buff: Start With $5",
    "Buff: Start With a Reroll Token",
    "Buff: Start With an Essence Token",
    "Buff: Choice of Symbols",
]



def build_unlock_items() -> List[str]:
    # Randomize symbols and normal items. Essences are intentionally not
    # AP unlocks in this build; they remain available as normal vanilla content.
    # Display all normal unlocks as one clean AP item name: "Unlock: Name".
    # Matryoshka Doll 2-5 are intentionally NOT separate unlocks. Receiving
    # "Unlock: Matryoshka Doll" enables all doll stages, while all doll stages
    # still keep their own Send checks.
    matryoshka_extra = {"Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5"}
    return (
        [f"Unlock: {name}" for name in SYMBOLS if name not in matryoshka_extra]
        + [f"Unlock: {name}" for name in NORMAL_ITEMS]
        + [f"Unlock: {name}" for name in ESSENCES]
    )


UNLOCK_ITEMS: List[str] = build_unlock_items()
# If bundles are set to 2 per bundle, this is the maximum bundle count needed.
MAX_BUNDLE_COUNT = (len(UNLOCK_ITEMS) + 1) // 2
BUNDLE_ITEMS: List[str] = [f"{BUNDLE_ITEM_PREFIX} {i}" for i in range(1, MAX_BUNDLE_COUNT + 1)]
FLOOR_UNLOCK_ITEMS: List[str] = [f"Unlock Floor {i}" for i in range(1, 21)]

# V10 generation fix:
# Unlock rewards need to count for Archipelago logic, because Send: locations
# are gated by receiving the matching unlock. V8/V9 made them only Useful,
# which caused generation to run out of reachable locations. Combining the
# flags keeps them marked Useful while still letting AP place them logically.
UNLOCK_LOGIC_CLASSIFICATION = ItemClassification.progression | ItemClassification.useful

item_table: Dict[str, ItemData] = {}
for index, item_name in enumerate(UNLOCK_ITEMS):
    item_table[item_name] = ItemData(ITEM_BASE_ID + index, UNLOCK_LOGIC_CLASSIFICATION, "Unlock")

for bundle_index, item_name in enumerate(BUNDLE_ITEMS, start=len(item_table)):
    item_table[item_name] = ItemData(ITEM_BASE_ID + bundle_index, UNLOCK_LOGIC_CLASSIFICATION, "Bundle")

for floor_index, item_name in enumerate(FLOOR_UNLOCK_ITEMS, start=len(item_table)):
    item_table[item_name] = ItemData(ITEM_BASE_ID + 5000 + floor_index, ItemClassification.progression, "Floor Unlock")

for item_name in TRAP_ITEMS:
    item_table[item_name] = ItemData(ITEM_BASE_ID + len(item_table), ItemClassification.trap, "Trap")

for item_name in BUFF_ITEMS:
    item_table[item_name] = ItemData(ITEM_BASE_ID + len(item_table), ItemClassification.useful, "Buff")

item_table[RASPBERRY_ITEM_NAME] = ItemData(ITEM_BASE_ID + len(item_table), ItemClassification.progression, "Raspberry")
item_table[PROGRESSIVE_AP_CHECKS_ITEM_NAME] = ItemData(ITEM_BASE_ID + len(item_table), ItemClassification.progression, "Progressive AP Checks")

for item_name in FILLER_ITEMS:
    item_table[item_name] = ItemData(ITEM_BASE_ID + len(item_table), ItemClassification.filler, "Filler")

item_name_groups = {
    "Symbols": frozenset(f"Unlock: {name}" for name in SYMBOLS if name not in {"Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5"}),
    "Items": frozenset(f"Unlock: {name}" for name in NORMAL_ITEMS),
    "Essences": frozenset(f"Unlock: {name}" for name in ESSENCES),
    "Unlocks": frozenset(UNLOCK_ITEMS),
    "Bundles": frozenset(BUNDLE_ITEMS),
    "Floor Unlocks": frozenset(FLOOR_UNLOCK_ITEMS),
    "Traps": frozenset(TRAP_ITEMS),
    "Buffs": frozenset(BUFF_ITEMS),
    "Filler": frozenset(FILLER_ITEMS),
    "Raspberry": frozenset({RASPBERRY_ITEM_NAME}),
    "Progressive AP Checks": frozenset({PROGRESSIVE_AP_CHECKS_ITEM_NAME}),
}
