from __future__ import annotations

import asyncio
import json
import os
import pkgutil
import random
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

try:
    from .Items import SYMBOLS, NORMAL_ITEMS, ESSENCES, PROGRESSIVE_AP_CHECKS_ITEM_NAME, RARE_SYMBOLS, VERY_RARE_SYMBOLS, RARE_ITEMS, VERY_RARE_ITEMS, RARE_ESSENCES, VERY_RARE_ESSENCES, BUFF_ITEMS, TRAP_ITEMS
    from .EasyContent import EASY_CONTENT, EASY_BY_NAME, EASY_NAME_TO_TYPE
except ImportError:
    from Items import SYMBOLS, NORMAL_ITEMS, ESSENCES, PROGRESSIVE_AP_CHECKS_ITEM_NAME, RARE_SYMBOLS, VERY_RARE_SYMBOLS, RARE_ITEMS, VERY_RARE_ITEMS, RARE_ESSENCES, VERY_RARE_ESSENCES, BUFF_ITEMS, TRAP_ITEMS
    from EasyContent import EASY_CONTENT, EASY_BY_NAME, EASY_NAME_TO_TYPE

try:
    from .lbal_pck_patcher import auto_patch_lbal_pck, restore_original_lbal_pck, find_lbal_pck
except ImportError:
    try:
        from lbal_pck_patcher import auto_patch_lbal_pck, restore_original_lbal_pck, find_lbal_pck
    except ImportError:
        auto_patch_lbal_pck = None
        restore_original_lbal_pck = None
        find_lbal_pck = None

import Utils
from CommonClient import (
    ClientCommandProcessor,
    CommonContext,
    get_base_parser,
    gui_enabled,
    handle_url_arg,
    logger,
    server_loop,
)
from NetUtils import ClientStatus, NetworkItem

GAME_NAME = "Luck be a Landlord"
BRIDGE_FOLDER_NAME = "LuckBeALandlordAP"


def get_bridge_path() -> Path:
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / BRIDGE_FOLDER_NAME
    return Path.home() / ".local" / "share" / BRIDGE_FOLDER_NAME


def get_godot_userdata_path() -> Path:
    """Luck be a Landlord user:// folder on Windows for Godot builds.

    The game/mod usually sees this as user://ap_state.json, which maps to:
    %APPDATA%/Godot/app_userdata/Luck be a Landlord/ap_state.json
    """
    if os.name == "nt" and os.environ.get("APPDATA"):
        return Path(os.environ["APPDATA"]) / "Godot" / "app_userdata" / "Luck be a Landlord"
    return Path.home() / ".local" / "share" / "godot" / "app_userdata" / "Luck be a Landlord"


def get_packaged_ap_check_png() -> Optional[bytes]:
    try:
        data = pkgutil.get_data(__package__ or "luck_be_a_landlord", "ap_check.png")
        if data:
            return data
    except Exception:
        pass
    try:
        return (Path(__file__).with_name("ap_check.png")).read_bytes()
    except Exception:
        return None


def ensure_ap_check_art_files() -> None:
    """Write AP Check art where the patched PCK and user mod can read it."""
    image_bytes = get_packaged_ap_check_png()
    if not image_bytes:
        return
    targets = [
        get_bridge_path() / "ap_check.png",
        get_godot_userdata_path() / "ap_check.png",
        get_godot_userdata_path() / "mods" / "Archipelago AP" / "art" / "ap_check.png",
    ]
    for target in targets:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_bytes() != image_bytes:
                target.write_bytes(image_bytes)
        except Exception:
            pass


def atomic_write_json(path: Path, data: Any) -> bool:
    """Write JSON without crashing if the game/editor briefly locks the file.

    Windows can lock files when VS Code, Notepad, Godot, or the game reads them.
    Use a unique temp file and retry so the AP client keeps running instead of
    spamming PermissionError / WinError 32.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    last_exc: Optional[BaseException] = None

    for attempt in range(12):
        tmp = path.with_name(f"{path.name}.{os.getpid()}.{int(time.time() * 1000)}.{attempt}.tmp")
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, path)
            return True
        except (PermissionError, OSError) as exc:
            last_exc = exc
            try:
                if tmp.exists():
                    tmp.unlink()
            except OSError:
                pass
            time.sleep(0.05 + attempt * 0.03)

    logger.warning("Could not write %s because another process is using it: %s", path, last_exc)
    return False


def read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return default


def delete_if_exists(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass




def _gd_quote(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _gd_array(values: Iterable[str]) -> str:
    return "[" + ", ".join(_gd_quote(v) for v in values) + "]"


SPECIAL_SYMBOL_TYPES: Dict[str, str] = {
    "Golden Arrow": "golden_arrow",
    "Silver Arrow": "silver_arrow",
    "Bronze Arrow": "bronze_arrow",
    "Clubs": "clubs",
    "Spades": "spades",
    "Hearts": "hearts",
    "Diamonds": "diamonds",
    "Three-Sided Die": "d3",
    "Five-Sided Die": "d5",
    "Eldritch Creature": "eldritch_beast",
    "Piñata": "pinata",
    "Buffing Capsule": "buffing_powder",
    "Hustling Capsule": "hustler",
    "Matryoshka Doll": "matryoshka_doll_1",
    "Matryoshka Doll 2": "matryoshka_doll_2",
    "Matryoshka Doll 3": "matryoshka_doll_3",
    "Matryoshka Doll 4": "matryoshka_doll_4",
    "Matryoshka Doll 5": "matryoshka_doll_5",
    "Geologist": "archaeologist",
    "Diamond": "diamond",
    "Wealthy Capsule": "item_capsule",
}

SPECIAL_ITEM_TYPES: Dict[str, str] = {
    "5th Ace": "fifth_ace",
    "Kyle the Kernite": "kyle_the_kernite",
    "Billionaire": "billionaire",
    "Cleaning Rag": "cleaning_rag",
    "Frying Pan": "frying_pan",
    "Joker": "joker",
    "Barrel of Dwarves": "barrel_o_dwarves",
    "Four-leaf clover": "four_leaf_clover",
    "Jack-o'-lantern": "jackolantern",
    "X-ray Machine": "x_ray_machine",
    # Vanilla LBAL internal IDs that do not match display-name snake_case.
    "Black Suits": "blue_suits",
    "Big Symbol Bomb": "symbol_bomb_big",
    "Quantum Symbol Bomb": "symbol_bomb_quantum",
    "The Tortoise and the Hare": "turtle_and_rabbit",
    "Small Symbol Bomb": "symbol_bomb_small",
    "Very Big Symbol Bomb": "symbol_bomb_very_big",
    "Fish Tank": "fish_bowl",
    # V81/V83: extra aliases so AP item targets actually appear in LBAL pools.
    "Piggy Bank": "piggy_bank",
    "Cursed Katana": "cursed_katana",
    "Bar of Soap": "bar_of_soap",
    "Removal Capsule": "removal_capsule",
    "Lucky Capsule": "lucky_capsule",
}

# Some LBAL versions/mod builds use slightly different internal type IDs for
# a few symbols/items than the simple display-name -> snake_case conversion.
# Include aliases in generated AP floors so these AP unlocks actually appear
# in-game once received, instead of only showing in the tracker.
SYMBOL_TYPE_ALIASES: Dict[str, List[str]] = {
    # Dice choices must use d3/d5. Face textures are added animation-only in the floor writer.
    "Three-Sided Die": ["d3"],
    "Five-Sided Die": ["d5"],
    # Arrow symbols use direction variants internally. Include the variants so
    # Golden/Silver/Bronze Arrow can rotate and apply their real vanilla effect.
    "Golden Arrow": ["golden_arrow", "golden_arrow1", "golden_arrow2", "golden_arrow3", "golden_arrow4", "golden_arrow5", "golden_arrow6", "golden_arrow7", "golden_arrow8"],
    "Silver Arrow": ["silver_arrow", "silver_arrow1", "silver_arrow2", "silver_arrow3", "silver_arrow4", "silver_arrow5", "silver_arrow6", "silver_arrow7", "silver_arrow8"],
    "Bronze Arrow": ["bronze_arrow", "bronze_arrow1", "bronze_arrow2", "bronze_arrow3", "bronze_arrow4", "bronze_arrow5", "bronze_arrow6", "bronze_arrow7", "bronze_arrow8"],

    # Suit descriptions such as Flush can reference these icons even if the
    # AP pool has not unlocked every suit yet.
    "Clubs": ["club", "clubs"],
    "Spades": ["spade", "spades"],
    "Hearts": ["heart", "hearts"],
    "Diamonds": ["diamond", "diamonds"],
    "Buffing Capsule": ["buffing_capsule", "buffing_powder"],
    "Hustling Capsule": ["hustling_capsule", "hustler"],
    "Geologist": ["archaeologist", "geologist"],
    "Diamond": ["diamond"],
    "Wealthy Capsule": ["lucky_capsule", "wealthy_capsule"],
}

ITEM_TYPE_ALIASES: Dict[str, List[str]] = {
    # Black Suits' real vanilla ID is blue_suits. Keep older aliases too so old logs/mods still work.
    "Black Suits": ["blue_suits", "black_suits", "black_suit"],
    "Red Suits": ["red_suits", "red_suit"],
    # Symbol Bombs use symbol_bomb_* internally, not *_symbol_bomb.
    "Big Symbol Bomb": ["symbol_bomb_big", "big_symbol_bomb", "big_bomb"],
    "Quantum Symbol Bomb": ["symbol_bomb_quantum", "quantum_symbol_bomb", "quantum_bomb"],
    "The Tortoise and the Hare": ["turtle_and_rabbit", "the_tortoise_and_the_hare", "tortoise_and_hare", "tortoise_hare"],
    "Small Symbol Bomb": ["symbol_bomb_small", "small_symbol_bomb", "small_bomb"],
    "Very Big Symbol Bomb": ["symbol_bomb_very_big", "very_big_symbol_bomb", "very_big_bomb"],
    "Kyle the Kernite": ["kyle_the_kernite", "kyle", "kernite"],
    "Fish Tank": ["fish_bowl", "fish_tank", "fish_tank_item"],
    "Piggy Bank": ["piggy_bank", "piggybank", "piggy_bank_item", "item_piggy_bank"],
    "Cursed Katana": ["cursed_katana", "katana", "cursed_sword", "item_cursed_katana"],
    "Bar of Soap": ["bar_of_soap", "soap", "soap_bar", "item_bar_of_soap"],
    "Removal Capsule": ["removal_capsule", "capsule_removal", "remove_capsule", "capsule_remove"],
    "Lucky Capsule": ["lucky_capsule", "capsule_lucky"],
    "Conveyor Belt": ["conveyor_belt", "belt_conveyor"],
    "Fruit Basket": ["fruit_basket", "basket_fruit"],
    "Shattered Mirror": ["shattered_mirror", "mirror_shattered"],
}


def _extend_unique(target: List[str], values: Iterable[str]) -> None:
    for value in values:
        if value and value not in target:
            target.append(value)

AP_BYPASS_SYMBOLS: Set[str] = set()  # Symbols in this set are ignored by the AP floor writer.
AP_SPAWNED_SYMBOLS: Set[str] = {
    "Apple",
    "Banana",
    "Cherry",
    "Coconut",
    "Flower",
    "Orange",
    "Peach",
    "Pear",
    "Seed",
    "Strawberry",
    "Void Fruit",
    "Watermelon",
    "Amethyst",
    "Diamond",
    "Emerald",
    "Ruby",
    "Sapphire",
    "Pearl",
    "Shiny Pebble",
    "Dud",
    "Hex of Destruction",
    "Ninja",
    "Turtle",
    "Cultist",
    "Crab",
    "Candy",
    "Bubble",
    "Coin",
    "Milk",
    "Beer",
    "Wine",
    # Needed for item effects such as Grave Robber. These are allowed as
    # effect-created symbols but the live PCK filter still keeps them out of
    # normal Add Symbol choices until AP allows them.
    "Urn",
    "Big Urn",
    "Spirit",
}


SPECIAL_ESSENCE_TYPES: Dict[str, str] = {
    "5th Ace Essence": "fifth_ace_essence",
    "Kyle the Kernite Essence": "kyle_the_kernite_essence",
    "Billionaire Essence": "billionaire_essence",
    "Cleaning Rag Essence": "cleaning_rag_essence",
    "Frying Pan Essence": "frying_pan_essence",
    "Joker Essence": "joker_essence",
    "Barrel of Dwarves Essence": "barrel_o_dwarves_essence",
    "Four-leaf clover Essence": "four_leaf_clover_essence",
    "Jack-o'-lantern Essence": "jackolantern_essence",
    "X-ray Machine Essence": "x_ray_machine_essence",
    "Small Symbol Bomb Essence": "symbol_bomb_small_essence",
    "Big Symbol Bomb Essence": "symbol_bomb_big_essence",
    "Very Big Symbol Bomb Essence": "symbol_bomb_very_big_essence",
    "Black Suits Essence": "blue_suits_essence",
    "The Tortoise and the Hare Essence": "turtle_and_rabbit_essence",
    "Fish Tank Essence": "fish_bowl_essence",
    "Quantum Symbol Bomb Essence": "symbol_bomb_quantum_essence",
    # V81: keep these essences working across LBAL internal naming variants.
    "Cursed Katana Essence": "cursed_katana_essence",
    "Piggy Bank Essence": "piggy_bank_essence",
}

# Essences are rolled through the item pool in LBAL, and several essence
# ModData IDs do not match simple display-name snake_case. Include every known
# vanilla spelling so an AP-unlocked essence is actually allowed to appear.
ESSENCE_TYPE_ALIASES: Dict[str, List[str]] = {
    "Small Symbol Bomb Essence": ["symbol_bomb_small_essence", "small_symbol_bomb_essence", "small_bomb_essence", "essence_symbol_bomb_small"],
    "Big Symbol Bomb Essence": ["symbol_bomb_big_essence", "big_symbol_bomb_essence", "big_bomb_essence", "essence_symbol_bomb_big"],
    "Very Big Symbol Bomb Essence": ["symbol_bomb_very_big_essence", "very_big_symbol_bomb_essence", "very_big_bomb_essence", "essence_symbol_bomb_very_big"],
    "Black Suits Essence": ["blue_suits_essence", "black_suits_essence", "black_suit_essence", "essence_blue_suits", "essence_black_suits"],
    "The Tortoise and the Hare Essence": ["turtle_and_rabbit_essence", "the_tortoise_and_the_hare_essence", "tortoise_and_hare_essence", "tortoise_hare_essence", "essence_turtle_and_rabbit"],
    "Kyle the Kernite Essence": ["kyle_the_kernite_essence", "kyle_essence", "kernite_essence", "essence_kyle"],
    "Fish Tank Essence": ["fish_bowl_essence", "fish_tank_essence", "fish_bowl_item_essence", "essence_fish_bowl", "essence_fish_tank"],
    "Quantum Symbol Bomb Essence": ["symbol_bomb_quantum_essence", "quantum_symbol_bomb_essence", "quantum_bomb_essence", "essence_symbol_bomb_quantum"],
    "Cursed Katana Essence": ["cursed_katana_essence", "essence_cursed_katana", "katana_essence", "cursed_sword_essence", "essence_katana"],
    "Piggy Bank Essence": ["piggy_bank_essence", "essence_piggy_bank", "piggybank_essence", "piggy_bank_item_essence"],
    "Guillotine Essence": ["guillotine_essence", "essence_guillotine"],
    "Oswald the Monkey Essence": ["oswald_the_monkey_essence", "oswald_essence", "essence_oswald_the_monkey", "essence_oswald"],
    "Nori the Rabbit Essence": ["nori_the_rabbit_essence", "nori_essence", "essence_nori_the_rabbit", "essence_nori"],
}

AP_EFFECT_ITEM_TO_EFFECT: Dict[str, str] = {
    # Legacy names kept for compatibility with old seeds.
    "Trap: Set Money to 1": "set_money_to_1",
    "Trap: No Score Next Spin": "no_score_next_spin",
    "Buff: Permanent Extra Spin Token": "permanent_extra_spin_token",
    "Buff: Permanent Extra Destroy Token": "permanent_extra_destroy_token",
    # V139 filler replacement buffs/traps.
    "Buff: Start With a Destroy Token": "start_destroy_token",
    "Buff: Start With $5": "start_5_dollars",
    "Buff: Start With a Reroll Token": "start_reroll_token",
    "Buff: Start With an Essence Token": "start_essence_token",
    "Buff: Choice of Symbols": "choice_symbols",
    # Backward compatibility for old generated rooms/YAML using the old name.
    "Buff: Choice of 20 Symbols": "choice_symbols",
    "Buff: Choice of Symbols": "choice_symbols",
    "Trap: Half Money": "half_money",
    "Trap: Force Payment": "force_payment",
    "Trap: Add Dud Symbol": "add_dud_symbol",
}

# V84: exact vanilla LBAL type IDs extracted from the uploaded game PCK JSON files.
# These override display-name snake_case guesses, so tracker targets use the
# real IDs from res://JSON/Symbols, res://JSON/Items, and res://JSON/Essences.
PCK_EXACT_SYMBOL_TYPES: Dict[str, str] = {'Amethyst': 'amethyst',
 'Anchor': 'anchor',
 'Apple': 'apple',
 'Banana': 'banana',
 'Banana Peel': 'banana_peel',
 'Bar of Soap': 'bar_of_soap',
 'Bartender': 'bartender',
 'Bear': 'bear',
 'Beastmaster': 'beastmaster',
 'Bee': 'bee',
 'Beehive': 'beehive',
 'Beer': 'beer',
 'Big Ore': 'big_ore',
 'Big Urn': 'big_urn',
 'Billionaire': 'billionaire',
 'Bounty Hunter': 'bounty_hunter',
 'Bronze Arrow': 'bronze_arrow',
 'Bubble': 'bubble',
 'Buffing Capsule': 'buffing_powder',
 'Candy': 'candy',
 'Card Shark': 'card_shark',
 'Cat': 'cat',
 'Cheese': 'cheese',
 'Chef': 'chef',
 'Chemical Seven': 'chemical_seven',
 'Cherry': 'cherry',
 'Chick': 'chick',
 'Chicken': 'chicken',
 'Clubs': 'clubs',
 'Coal': 'coal',
 'Coconut': 'coconut',
 'Coconut Half': 'coconut_half',
 'Coin': 'coin',
 'Comedian': 'comedian',
 'Cow': 'cow',
 'Crab': 'crab',
 'Crow': 'crow',
 'Cultist': 'cultist',
 'Dame': 'dame',
 'Diamond': 'diamond',
 'Diamonds': 'diamonds',
 'Diver': 'diver',
 'Dog': 'dog',
 'Dove': 'dove',
 'Dwarf': 'dwarf',
 'Egg': 'egg',
 'Eldritch Creature': 'eldritch_beast',
 'Emerald': 'emerald',
 'Empty': 'empty',
 'Essence Capsule': 'essence_capsule',
 'Farmer': 'farmer',
 'Five-Sided Die': 'd5',
 'Flower': 'flower',
 'Frozen Fossil': 'frozen_fossil',
 'Gambler': 'gambler',
 'General Zaroff': 'general_zaroff',
 'Geologist': 'archaeologist',
 'Golden Arrow': 'golden_arrow',
 'Golden Egg': 'golden_egg',
 'Goldfish': 'goldfish',
 'Golem': 'golem',
 'Goose': 'goose',
 'Hearts': 'hearts',
 'Hex of Destruction': 'hex_of_destruction',
 'Hex of Draining': 'hex_of_draining',
 'Hex of Emptiness': 'hex_of_emptiness',
 'Hex of Hoarding': 'hex_of_hoarding',
 'Hex of Midas': 'hex_of_midas',
 'Hex of Tedium': 'hex_of_tedium',
 'Hex of Thievery': 'hex_of_thievery',
 'Highlander': 'highlander',
 'Honey': 'honey',
 'Hooligan': 'hooligan',
 'Hustling Capsule': 'hustler',
 'Jellyfish': 'jellyfish',
 'Joker': 'joker',
 'Key': 'key',
 'King Midas': 'king_midas',
 'Light Bulb': 'light_bulb',
 'Lockbox': 'lockbox',
 'Lucky Capsule': 'lucky_capsule',
 'Magic Key': 'magic_key',
 'Magpie': 'magpie',
 'Martini': 'martini',
 'Matryoshka Doll': 'matryoshka_doll_1',
 'Matryoshka Doll 2': 'matryoshka_doll_2',
 'Matryoshka Doll 3': 'matryoshka_doll_3',
 'Matryoshka Doll 4': 'matryoshka_doll_4',
 'Matryoshka Doll 5': 'matryoshka_doll_5',
 'Mega Chest': 'mega_chest',
 'Midas Bomb': 'midas_bomb',
 'Milk': 'milk',
 'Mine': 'mine',
 'Miner': 'miner',
 'Monkey': 'monkey',
 'Moon': 'moon',
 'Mouse': 'mouse',
 'Mrs. Fruit': 'mrs_fruit',
 'Ninja': 'ninja',
 'Omelette': 'omelette',
 'Orange': 'orange',
 'Ore': 'ore',
 'Owl': 'owl',
 'Oyster': 'oyster',
 'Peach': 'peach',
 'Pear': 'pear',
 'Pearl': 'pearl',
 'Pirate': 'pirate',
 'Piñata': 'pinata',
 'Present': 'present',
 'Pufferfish': 'pufferfish',
 'Rabbit': 'rabbit',
 'Rabbit Fluff': 'rabbit_fluff',
 'Rain': 'rain',
 'Removal Capsule': 'removal_capsule',
 'Reroll Capsule': 'reroll_capsule',
 'Robin Hood': 'robin_hood',
 'Ruby': 'ruby',
 'Safe': 'safe',
 'Sand Dollar': 'sand_dollar',
 'Sapphire': 'sapphire',
 'Seed': 'seed',
 'Shiny Pebble': 'shiny_pebble',
 'Silver Arrow': 'silver_arrow',
 'Sloth': 'sloth',
 'Snail': 'snail',
 'Spades': 'spades',
 'Spirit': 'spirit',
 'Strawberry': 'strawberry',
 'Sun': 'sun',
 'Target': 'target',
 'Tedium Capsule': 'tedium_capsule',
 'Thief': 'thief',
 'Three-Sided Die': 'd3',
 'Time Capsule': 'time_capsule',
 'Toddler': 'toddler',
 'Tomb': 'tomb',
 'Treasure Chest': 'treasure_chest',
 'Turtle': 'turtle',
 'Urn': 'urn',
 'Void Creature': 'void_creature',
 'Void Fruit': 'void_fruit',
 'Void Stone': 'void_stone',
 'Watermelon': 'watermelon',
 'Wealthy Capsule': 'item_capsule',
 'Wildcard': 'wildcard',
 'Wine': 'wine',
 'Witch': 'witch',
 'Wolf': 'wolf'}

PCK_EXACT_ITEM_TYPES: Dict[str, str] = {'5th Ace': 'fifth_ace',
 'Adoption Papers': 'adoption_papers',
 'Ancient Lizard Blade': 'ancient_lizard_blade',
 'Anthropology Degree': 'anthropology_degree',
 'Barrel of Dwarves': 'barrel_o_dwarves',
 'Big Symbol Bomb': 'symbol_bomb_big',
 'Birdhouse': 'birdhouse',
 'Black Cat': 'black_cat',
 'Black Pepper': 'black_pepper',
 'Black Suits': 'blue_suits',
 'Blue Pepper': 'blue_pepper',
 'Booster Pack': 'booster_pack',
 'Bowling Ball': 'bowling_ball',
 'Brown Pepper': 'brown_pepper',
 'Capsule Machine': 'capsule_machine',
 'Cardboard Box': 'cardboard_box',
 'Checkered Flag': 'checkered_flag',
 'Chicken Coop': 'chicken_coop',
 'Chili Powder': 'chili_powder',
 'Cleaning Rag': 'cleaning_rag',
 'Clear Sky': 'clear_sky',
 'Coffee': 'coffee',
 'Coin on a String': 'coin_on_a_string',
 'Comfy Pillow': 'comfy_pillow',
 'Compost Heap': 'compost_heap',
 'Conveyor Belt': 'conveyor_belt',
 'Copycat': 'copycat',
 'Credit Card': 'credit_card',
 'Cursed Katana': 'cursed_katana',
 'Cyan Pepper': 'cyan_pepper',
 'Dark Humor': 'dark_humor',
 "Devil's Deal": 'devils_deal',
 'Dishwasher': 'dishwasher',
 'Dwarven Anvil': 'dwarven_anvil',
 'Egg Carton': 'egg_carton',
 'Fertilizer': 'fertilizer',
 'Fish Tank': 'fish_bowl',
 'Flush': 'flush',
 'Four-leaf clover': 'four_leaf_clover',
 'Frozen Pizza': 'frozen_pizza',
 'Fruit Basket': 'fruit_basket',
 'Frying Pan': 'frying_pan',
 'Golden Carrot': 'golden_carrot',
 'Goldilocks': 'goldilocks',
 'Grave Robber': 'grave_robber',
 'Gray Pepper': 'gray_pepper',
 'Green Pepper': 'green_pepper',
 'Guillotine': 'guillotine',
 'Happy Hour': 'happy_hour',
 'Holy Water': 'holy_water',
 'Horseshoe': 'horseshoe',
 "Jack-o'-lantern": 'jackolantern',
 'Kyle the Kernite': 'kyle_the_kernite',
 'Lefty the Rabbit': 'lefty_the_rabbit',
 'Lemon': 'lemon',
 'Lime Pepper': 'lime_pepper',
 'Lint Roller': 'lint_roller',
 'Lockpick': 'lockpick',
 'Looting Glove': 'looting_glove',
 'Lucky Carrot': 'lucky_carrot',
 'Lucky Cat': 'lucky_cat',
 'Lucky Dice': 'lucky_dice',
 'Lucky Seven': 'lucky_seven',
 'Lunchbox': 'lunchbox',
 'Maxwell the Bear': 'maxwell_the_bear',
 'Mining Pick': 'mining_pick',
 'Mobius Strip': 'mobius_strip',
 'Ninja and Mouse': 'ninja_and_mouse',
 'Nori the Rabbit': 'nori_the_rabbit',
 'Oil Can': 'oil_can',
 'Oswald the Monkey': 'oswald_the_monkey',
 'Piggy Bank': 'piggy_bank',
 'Pink Pepper': 'pink_pepper',
 'Pizza the Cat': 'pizza_the_cat',
 'Pool Ball': 'pool_ball',
 'Popsicle': 'popsicle',
 'Protractor': 'protractor',
 'Purple Pepper': 'purple_pepper',
 'Quantum Symbol Bomb': 'symbol_bomb_quantum',
 'Quigley the Wolf': 'quigley_the_wolf',
 'Quiver': 'quiver',
 'Rain Cloud': 'rain_cloud',
 'Recycling': 'recycling',
 'Red Pepper': 'red_pepper',
 'Red Suits': 'red_suits',
 'Reroll': 'reroll',
 'Ricky the Banana': 'ricky_the_banana',
 'Ritual Candle': 'ritual_candle',
 'Rusty Gear': 'rusty_gear',
 'Shattered Mirror': 'shattered_mirror',
 'Shedding Season': 'shedding_season',
 'Shrine': 'shrine',
 'Small Symbol Bomb': 'symbol_bomb_small',
 'Sunglasses': 'sunglasses',
 'Swapping Device': 'swapping_device',
 'Swear Jar': 'swear_jar',
 'Tax Evasion': 'tax_evasion',
 'Telescope': 'telescope',
 'The Tortoise and the Hare': 'turtle_and_rabbit',
 'Time Machine': 'time_machine',
 'Treasure Map': 'treasure_map',
 'Triple Coins': 'triple_coins',
 'Undertaker': 'undertaker',
 'Very Big Symbol Bomb': 'symbol_bomb_very_big',
 'Void Party': 'void_party',
 'Void Portal': 'void_portal',
 'Wanted Poster': 'wanted_poster',
 'Watering Can': 'watering_can',
 'White Pepper': 'white_pepper',
 'X-ray Machine': 'x_ray_machine',
 'Yellow Pepper': 'yellow_pepper',
 "Zaroff's Contract": 'zaroffs_contract'}

PCK_EXACT_ESSENCE_TYPES: Dict[str, str] = {'5th Ace Essence': 'fifth_ace_essence',
 'Adoption Papers Essence': 'adoption_papers_essence',
 'Ancient Lizard Blade Essence': 'ancient_lizard_blade_essence',
 'Anthropology Degree Essence': 'anthropology_degree_essence',
 'Barrel of Dwarves Essence': 'barrel_o_dwarves_essence',
 'Big Symbol Bomb Essence': 'symbol_bomb_big_essence',
 'Birdhouse Essence': 'birdhouse_essence',
 'Black Cat Essence': 'black_cat_essence',
 'Black Pepper Essence': 'black_pepper_essence',
 'Black Suits Essence': 'blue_suits_essence',
 'Blue Pepper Essence': 'blue_pepper_essence',
 'Booster Pack Essence': 'booster_pack_essence',
 'Bowling Ball Essence': 'bowling_ball_essence',
 'Brown Pepper Essence': 'brown_pepper_essence',
 'Capsule Machine Essence': 'capsule_machine_essence',
 'Cardboard Box Essence': 'cardboard_box_essence',
 'Checkered Flag Essence': 'checkered_flag_essence',
 'Chicken Coop Essence': 'chicken_coop_essence',
 'Chili Powder Essence': 'chili_powder_essence',
 'Cleaning Rag Essence': 'cleaning_rag_essence',
 'Clear Sky Essence': 'clear_sky_essence',
 'Coffee Essence': 'coffee_essence',
 'Coin on a String Essence': 'coin_on_a_string_essence',
 'Comfy Pillow Essence': 'comfy_pillow_essence',
 'Compost Heap Essence': 'compost_heap_essence',
 'Conveyor Belt Essence': 'conveyor_belt_essence',
 'Copycat Essence': 'copycat_essence',
 'Credit Card Essence': 'credit_card_essence',
 'Cursed Katana Essence': 'cursed_katana_essence',
 'Cyan Pepper Essence': 'cyan_pepper_essence',
 'Dark Humor Essence': 'dark_humor_essence',
 "Devil's Deal Essence": 'devils_deal_essence',
 'Dishwasher Essence': 'dishwasher_essence',
 'Dwarven Anvil Essence': 'dwarven_anvil_essence',
 'Egg Carton Essence': 'egg_carton_essence',
 'Fertilizer Essence': 'fertilizer_essence',
 'Fish Tank Essence': 'fish_bowl_essence',
 'Flush Essence': 'flush_essence',
 'Four-leaf clover Essence': 'four_leaf_clover_essence',
 'Frozen Pizza Essence': 'frozen_pizza_essence',
 'Fruit Basket Essence': 'fruit_basket_essence',
 'Frying Pan Essence': 'frying_pan_essence',
 'Golden Carrot Essence': 'golden_carrot_essence',
 'Goldilocks Essence': 'goldilocks_essence',
 'Grave Robber Essence': 'grave_robber_essence',
 'Gray Pepper Essence': 'gray_pepper_essence',
 'Green Pepper Essence': 'green_pepper_essence',
 'Guillotine Essence': 'guillotine_essence',
 'Happy Hour Essence': 'happy_hour_essence',
 'Holy Water Essence': 'holy_water_essence',
 'Horseshoe Essence': 'horseshoe_essence',
 "Jack-o'-lantern Essence": 'jackolantern_essence',
 'Kyle the Kernite Essence': 'kyle_the_kernite_essence',
 'Lefty the Rabbit Essence': 'lefty_the_rabbit_essence',
 'Lemon Essence': 'lemon_essence',
 'Lime Pepper Essence': 'lime_pepper_essence',
 'Lint Roller Essence': 'lint_roller_essence',
 'Lockpick Essence': 'lockpick_essence',
 'Looting Glove Essence': 'looting_glove_essence',
 'Lucky Carrot Essence': 'lucky_carrot_essence',
 'Lucky Cat Essence': 'lucky_cat_essence',
 'Lucky Dice Essence': 'lucky_dice_essence',
 'Lucky Seven Essence': 'lucky_seven_essence',
 'Lunchbox Essence': 'lunchbox_essence',
 'Maxwell the Bear Essence': 'maxwell_the_bear_essence',
 'Mining Pick Essence': 'mining_pick_essence',
 'Mobius Strip Essence': 'mobius_strip_essence',
 'Ninja and Mouse Essence': 'ninja_and_mouse_essence',
 'Nori the Rabbit Essence': 'nori_the_rabbit_essence',
 'Oil Can Essence': 'oil_can_essence',
 'Oswald the Monkey Essence': 'oswald_the_monkey_essence',
 'Piggy Bank Essence': 'piggy_bank_essence',
 'Pink Pepper Essence': 'pink_pepper_essence',
 'Pizza the Cat Essence': 'pizza_the_cat_essence',
 'Pool Ball Essence': 'pool_ball_essence',
 'Popsicle Essence': 'popsicle_essence',
 'Protractor Essence': 'protractor_essence',
 'Purple Pepper Essence': 'purple_pepper_essence',
 'Quantum Symbol Bomb Essence': 'symbol_bomb_quantum_essence',
 'Quigley the Wolf Essence': 'quigley_the_wolf_essence',
 'Quiver Essence': 'quiver_essence',
 'Rain Cloud Essence': 'rain_cloud_essence',
 'Recycling Essence': 'recycling_essence',
 'Red Pepper Essence': 'red_pepper_essence',
 'Red Suits Essence': 'red_suits_essence',
 'Reroll Essence': 'reroll_essence',
 'Ricky the Banana Essence': 'ricky_the_banana_essence',
 'Ritual Candle Essence': 'ritual_candle_essence',
 'Rusty Gear Essence': 'rusty_gear_essence',
 'Shattered Mirror Essence': 'shattered_mirror_essence',
 'Shedding Season Essence': 'shedding_season_essence',
 'Shrine Essence': 'shrine_essence',
 'Small Symbol Bomb Essence': 'symbol_bomb_small_essence',
 'Sunglasses Essence': 'sunglasses_essence',
 'Swapping Device Essence': 'swapping_device_essence',
 'Swear Jar Essence': 'swear_jar_essence',
 'Tax Evasion Essence': 'tax_evasion_essence',
 'Telescope Essence': 'telescope_essence',
 'The Tortoise and the Hare Essence': 'turtle_and_rabbit_essence',
 'Time Machine Essence': 'time_machine_essence',
 'Treasure Map Essence': 'treasure_map_essence',
 'Triple Coins Essence': 'triple_coins_essence',
 'Undertaker Essence': 'undertaker_essence',
 'Very Big Symbol Bomb Essence': 'symbol_bomb_very_big_essence',
 'Void Party Essence': 'void_party_essence',
 'Void Portal Essence': 'void_portal_essence',
 'Wanted Poster Essence': 'wanted_poster_essence',
 'Watering Can Essence': 'watering_can_essence',
 'White Pepper Essence': 'white_pepper_essence',
 'X-ray Machine Essence': 'x_ray_machine_essence',
 'Yellow Pepper Essence': 'yellow_pepper_essence',
 "Zaroff's Contract Essence": 'zaroffs_contract_essence'}


def _display_to_lbal_type(name: str, kind: str) -> str:
    if name in EASY_NAME_TO_TYPE:
        return EASY_NAME_TO_TYPE[name]
    if kind == "symbol" and name in PCK_EXACT_SYMBOL_TYPES:
        return PCK_EXACT_SYMBOL_TYPES[name]
    if kind == "item" and name in PCK_EXACT_ITEM_TYPES:
        return PCK_EXACT_ITEM_TYPES[name]
    if kind == "essence" and name in PCK_EXACT_ESSENCE_TYPES:
        return PCK_EXACT_ESSENCE_TYPES[name]
    if kind == "symbol" and name in SPECIAL_SYMBOL_TYPES:
        return SPECIAL_SYMBOL_TYPES[name]
    if kind == "item" and name in SPECIAL_ITEM_TYPES:
        return SPECIAL_ITEM_TYPES[name]
    if kind == "essence" and name in SPECIAL_ESSENCE_TYPES:
        return SPECIAL_ESSENCE_TYPES[name]
    value = name.strip().lower()
    replacements = {
        "'": "",
        "’": "",
        ".": "",
        ",": "",
        ":": "",
        "-": "_",
        " ": "_",
        "ñ": "n",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    while "__" in value:
        value = value.replace("__", "_")
    return _safe_lbal_type(value.strip("_"))


def _has_unsafe_large_numeric_suffix(type_id: str) -> bool:
    """LBAL/Godot can overflow on icon IDs like golem_2895537308.

    Those are usually raw Workshop/internal mod IDs without matching art in the
    generated AP mod. Do not inject them into included/excluded/live pools.
    """
    value = str(type_id or "")
    match = re.search(r"_(\d{10,})($|_)", value)
    if not match:
        return False
    try:
        return int(match.group(1)) > 2147483647
    except ValueError:
        return True


def _safe_lbal_type(type_id: str) -> str:
    value = str(type_id or "").strip()
    return "" if _has_unsafe_large_numeric_suffix(value) else value



DICE_FACE_TEXTURE_TYPES: Set[str] = {
    "dice1", "dice2", "dice3", "dice4", "dice5",
    "d3_1", "d3_2", "d3_3",
}


def _canonical_symbol_type_v55(type_id: str) -> str:
    value = str(type_id or "")
    # Only map display-name/bad AP aliases to the real vanilla dice symbols.
    # Do NOT map dice1-5 or d3_1-3 here; those are animation face textures and
    # must stay available for the dice roll animation.
    dice_aliases = {
        "three_sided_die": "d3",
        "three_sided_dice": "d3",
        "three_sided_die_symbol": "d3",
        "five_sided_die": "d5",
        "five_sided_dice": "d5",
        "five_sided_die_symbol": "d5",
        "dice": "d5",
        "die": "d5",
    }
    return dice_aliases.get(value, value)


def _dice_animation_types_v58(values: Iterable[str]) -> List[str]:
    """Extra vanilla texture IDs needed by dice roll animations.

    These must be present on the generated floor so Slot Icon can cycle textures,
    but they should not be separately offered as AP Add Symbol choices.
    """
    value_set = set(str(v) for v in values)
    extra: List[str] = []
    if "d5" in value_set:
        extra.extend(["dice1", "dice2", "dice3", "dice4", "dice5"])
    if "d3" in value_set:
        extra.extend(["d3_1", "d3_2", "d3_3"])
    return extra


def _filter_safe_lbal_types(values: Iterable[str]) -> List[str]:
    result: List[str] = []
    for value in values:
        safe = _safe_lbal_type(str(value))
        if safe and safe not in result:
            result.append(safe)
    return result


def split_unlocks(unlocks: Iterable[str]) -> Dict[str, List[str]]:
    """Split AP unlock item names into game-facing symbol/item/essence lists."""
    result: Dict[str, List[str]] = {"symbols": [], "items": [], "essences": [], "other": []}
    matryoshka_all = ["Matryoshka Doll", "Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5"]
    for unlock in unlocks:
        if unlock.startswith("Unlock: "):
            name = unlock.removeprefix("Unlock: ")
            if name == "Matryoshka Doll":
                # V75: only the default/base Matryoshka Doll should be in Add Symbol.
                # The vanilla symbol evolves through Matryoshka Doll 2-5 in-game,
                # and _send_checks_for_unlock() still exposes all five Send checks.
                if name not in AP_BYPASS_SYMBOLS:
                    result["symbols"].append(name)
            elif name in SYMBOLS:
                if name in AP_BYPASS_SYMBOLS:
                    continue
                result["symbols"].append(name)
            elif name in NORMAL_ITEMS:
                result["items"].append(name)
            elif name in ESSENCES:
                result["essences"].append(name)
            else:
                result["other"].append(unlock)
        elif unlock.startswith("Unlock Symbol: "):
            name = unlock.removeprefix("Unlock Symbol: ")
            if name == "Matryoshka Doll":
                # V75: keep only the base/default doll in the pool.
                if name not in AP_BYPASS_SYMBOLS:
                    result["symbols"].append(name)
            elif name in SYMBOLS and name not in AP_BYPASS_SYMBOLS:
                result["symbols"].append(name)
            else:
                result["other"].append(unlock)
        elif unlock.startswith("Unlock Item: "):
            name = unlock.removeprefix("Unlock Item: ")
            if name in NORMAL_ITEMS:
                result["items"].append(name)
            elif name in ESSENCES:
                result["essences"].append(name)
            else:
                result["other"].append(unlock)
        elif unlock.startswith("Unlock Essence: "):
            result["essences"].append(unlock.removeprefix("Unlock Essence: "))
        elif unlock not in {"Progressive Filler", "Progressive Nothing", "Strawberry"}:
            result["other"].append(unlock)
    for key in result:
        # Keep deterministic order for the game mod.
        result[key] = sorted(set(result[key]))
    return result

def all_floors() -> List[int]:
    return list(range(1, 21))


def _normalise_symbol_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _match_symbol_name(value: str) -> Optional[str]:
    wanted = _normalise_symbol_name(value)
    if not wanted:
        return None
    exact = {_normalise_symbol_name(symbol): symbol for symbol in SYMBOLS}
    if wanted in exact:
        return exact[wanted]

    # Allow useful partial symbol matching when unambiguous.
    partial_matches = [symbol for symbol in SYMBOLS if wanted in _normalise_symbol_name(symbol)]
    if len(partial_matches) == 1:
        return partial_matches[0]
    return None


class LuckCommandProcessor(ClientCommandProcessor):
    def _disabled_cmd_bridge(self) -> bool:
        """Show the folder used to communicate with the Luck be a Landlord mod."""
        self.output(f"Bridge folder: {self.ctx.bridge_path}")
        self.output(f"Godot user folder: {self.ctx.godot_path}")
        return True



    def _ap_lbal_join_command_args_v63(self, *parts: str) -> str:
        """Accept AP command handlers that pass one or multiple words."""
        return " ".join(str(p) for p in parts if str(p).strip()).strip()

    def _cmd_boost(self, mode: str = "", *extra: str) -> bool:
        """Toggle the local unlockable chance boost override. Usage: /boost on, /boost off, /boost toggle, /boost auto, /boost status"""
        value = (self._ap_lbal_join_command_args_v63(mode, *extra) or "status").strip().lower()
        current = self.ctx._unlockable_chance_boost_enabled()
        source = "client override" if self.ctx._unlockable_chance_boost_override is not None else "slot default"

        if value in {"", "status"}:
            self.output(f"Unlockable chance boost: {'ON' if current else 'OFF'} ({source}).")
            self.output("Use /boost on, /boost off, /boost toggle, or /boost auto.")
            return True

        if value == "auto":
            self.ctx._unlockable_chance_boost_override = None
        elif value == "toggle":
            self.ctx._unlockable_chance_boost_override = not current
        elif value in {"on", "true", "1", "yes"}:
            self.ctx._unlockable_chance_boost_override = True
        elif value in {"off", "false", "0", "no"}:
            self.ctx._unlockable_chance_boost_override = False
        else:
            self.output("Usage: /boost on, /boost off, /boost toggle, /boost auto, /boost status")
            return False

        self.ctx.save_client_settings()
        self.ctx.write_state_file()
        self.ctx.write_generated_lbal_mod(force=True)
        effective = self.ctx._unlockable_chance_boost_enabled()
        source = "client override" if self.ctx._unlockable_chance_boost_override is not None else "slot default"
        self.output(f"Unlockable chance boost now {'ON' if effective else 'OFF'} ({source}).")
        self.output("Rewrote ap_state.json and regenerated the LBAL mod. New Add Symbol/Add Item choices should use this; reopen the choice screen or start a fresh AP floor if LBAL cached the current menu.")
        return True

    def _cmd_boostmode(self, mode: str = "", *extra: str) -> bool:
        """Set boost mode. Usage: /boostmode regular, /boostmode category, /boostmode rarity, /boostmode auto, /boostmode status"""
        value = (self._ap_lbal_join_command_args_v63(mode, *extra) or "status").strip().lower().replace("-", "_")
        current = self.ctx._unlockable_chance_boost_mode()
        source = "client override" if self.ctx._unlockable_chance_boost_mode_override is not None else "slot default"

        if value in {"", "status"}:
            self.output(f"Unlockable boost mode: {current} ({source}).")
            self.output("Use /boostmode regular, /boostmode category, /boostmode rarity, or /boostmode auto.")
            return True

        if value == "auto":
            self.ctx._unlockable_chance_boost_mode_override = None
        elif value in {"regular", "normal", "vanilla", "rarity_chance", "regular_rarity"}:
            self.ctx._unlockable_chance_boost_mode_override = "regular"
        elif value in {"category", "cat", "just_category"}:
            self.ctx._unlockable_chance_boost_mode_override = "category"
        elif value in {"rarity", "category_and_rarity", "category_rarity", "per_rarity", "rarity_and_category"}:
            self.ctx._unlockable_chance_boost_mode_override = "category_and_rarity"
        else:
            self.output("Usage: /boostmode regular, /boostmode category, /boostmode rarity, /boostmode auto, /boostmode status")
            return False

        self.ctx.save_client_settings()
        self.ctx.write_state_file()
        self.ctx.write_generated_lbal_mod(force=True)
        effective = self.ctx._unlockable_chance_boost_mode()
        source = "client override" if self.ctx._unlockable_chance_boost_mode_override is not None else "slot default"
        self.output(f"Unlockable boost mode now {effective} ({source}).")
        self.output("Rewrote ap_state.json and regenerated the LBAL mod.")
        return True

    def _cmd_raritypool(self, mode: str = "", *extra: str) -> bool:
        """Toggle rare/very-rare in-game pool override. Usage: /raritypool on, /raritypool off, /raritypool toggle, /raritypool auto, /raritypool status"""
        value = (self._ap_lbal_join_command_args_v63(mode, *extra) or "status").strip().lower()
        current = self.ctx._rare_very_rare_pool_enabled()
        source = "client override" if self.ctx._rare_very_rare_pool_override is not None else "slot default"

        if value in {"", "status"}:
            self.output(f"Rare/Very Rare in-game pool: {'ON' if current else 'OFF'} ({source}).")
            self.output("Use /raritypool on, /raritypool off, /raritypool toggle, or /raritypool auto.")
            return True

        if value == "auto":
            self.ctx._rare_very_rare_pool_override = None
        elif value == "toggle":
            self.ctx._rare_very_rare_pool_override = not current
        elif value in {"on", "true", "1", "yes", "enabled"}:
            self.ctx._rare_very_rare_pool_override = True
        elif value in {"off", "false", "0", "no", "disabled"}:
            self.ctx._rare_very_rare_pool_override = False
        else:
            self.output("Usage: /raritypool on, /raritypool off, /raritypool toggle, /raritypool auto, /raritypool status")
            return False

        self.ctx.save_client_settings()
        self.ctx.write_state_file()
        self.ctx.write_generated_lbal_mod(force=True)
        effective = self.ctx._rare_very_rare_pool_enabled()
        source = "client override" if self.ctx._rare_very_rare_pool_override is not None else "slot default"
        self.output(f"Rare/Very Rare in-game pool now {'ON' if effective else 'OFF'} ({source}).")
        self.output("Rewrote ap_state.json and regenerated the LBAL mod.")
        return True

    def _cmd_deaththreshold(self, which: str = "", value: str = "") -> bool:
        """Set DeathLink thresholds. Usage: /deaththreshold receive 2, /deaththreshold send 3, /deaththreshold auto"""
        target = (which or "status").strip().lower()
        val = (value or "").strip().lower()

        if target in {"", "status"}:
            receive_source = "client override" if self.ctx._deathlink_receive_threshold_override is not None else "slot default"
            send_source = "client override" if self.ctx._deathlink_send_threshold_override is not None else "slot default"
            self.output(f"DeathLink receive threshold: {self.ctx.deathlink_receive_threshold()} ({receive_source}).")
            self.output(f"DeathLink send threshold: {self.ctx.deathlink_send_threshold()} ({send_source}).")
            self.output("Usage: /deaththreshold receive 2, /deaththreshold send 3, /deaththreshold auto")
            return True

        if target in {"auto", "reset", "default"}:
            self.ctx._deathlink_receive_threshold_override = None
            self.ctx._deathlink_send_threshold_override = None
        elif target in {"receive", "received", "recv", "incoming", "in"}:
            if val in {"auto", "reset", "default"}:
                self.ctx._deathlink_receive_threshold_override = None
            else:
                try:
                    self.ctx._deathlink_receive_threshold_override = max(1, min(20, int(val)))
                except Exception:
                    self.output("Usage: /deaththreshold receive 2")
                    return False
        elif target in {"send", "sent", "out", "outgoing"}:
            if val in {"auto", "reset", "default"}:
                self.ctx._deathlink_send_threshold_override = None
            else:
                try:
                    self.ctx._deathlink_send_threshold_override = max(1, min(20, int(val)))
                except Exception:
                    self.output("Usage: /deaththreshold send 3")
                    return False
        else:
            self.output("Usage: /deaththreshold receive 2, /deaththreshold send 3, /deaththreshold auto")
            return False

        # Reset partial counters when changing thresholds so old pending counts
        # do not instantly trigger under the new value.
        self.ctx._incoming_death_pending_count = 0
        self.ctx._local_death_pending_count = 0
        self.ctx.save_client_settings()
        self.ctx.write_state_file()
        receive_source = "client override" if self.ctx._deathlink_receive_threshold_override is not None else "slot default"
        send_source = "client override" if self.ctx._deathlink_send_threshold_override is not None else "slot default"
        self.output(f"DeathLink receive threshold now {self.ctx.deathlink_receive_threshold()} ({receive_source}).")
        self.output(f"DeathLink send threshold now {self.ctx.deathlink_send_threshold()} ({send_source}).")
        return True

    def _cmd_deathlink(self, mode: str = "", *extra: str) -> bool:
        """Toggle the local DeathLink override. Usage: /deathlink on, /deathlink off, /deathlink toggle, /deathlink auto, /deathlink status"""
        value = (self._ap_lbal_join_command_args_v63(mode, *extra) or "status").strip().lower()
        current = self.ctx.deathlink_enabled()
        source = "client override" if self.ctx._deathlink_override is not None else "slot default"

        if value in {"", "status"}:
            self.output(f"DeathLink: {'ON' if current else 'OFF'} ({source}).")
            receive_source = "client override" if self.ctx._deathlink_receive_threshold_override is not None else "slot default"
            send_source = "client override" if self.ctx._deathlink_send_threshold_override is not None else "slot default"
            self.output(f"Receive threshold: {self.ctx.deathlink_receive_threshold()} ({receive_source}).")
            self.output(f"Send threshold: {self.ctx.deathlink_send_threshold()} ({send_source}).")
            self.output("Use /deathlink on, /deathlink off, /deathlink toggle, or /deathlink auto.")
            self.output("Use /deaththreshold receive 2 or /deaththreshold send 3 to change thresholds.")
            return True

        if value == "auto":
            self.ctx._deathlink_override = None
        elif value == "toggle":
            self.ctx._deathlink_override = not current
        elif value in {"on", "true", "1", "yes", "enabled"}:
            self.ctx._deathlink_override = True
        elif value in {"off", "false", "0", "no", "disabled"}:
            self.ctx._deathlink_override = False
        else:
            self.output("Usage: /deathlink on, /deathlink off, /deathlink toggle, /deathlink auto, /deathlink status")
            return False

        self.ctx.save_client_settings()
        self.ctx._incoming_death_pending_count = 0
        self.ctx._local_death_pending_count = 0
        if not self.ctx.deathlink_enabled():
            self.ctx.pending_deathlinks.clear()
            for receive_file in getattr(self.ctx, "_deathlink_receive_paths", []):
                delete_if_exists(receive_file)
            for send_file in getattr(self.ctx, "_deathlink_send_paths", []):
                delete_if_exists(send_file)
            for ack_file in getattr(self.ctx, "_deathlink_ack_paths", []):
                delete_if_exists(ack_file)

        self.ctx.write_state_file()
        Utils.async_start(self.ctx.update_deathlink_tag(), name="Luck DeathLink toggle")
        effective = self.ctx.deathlink_enabled()
        source = "client override" if self.ctx._deathlink_override is not None else "slot default"
        self.output(f"DeathLink now {'ON' if effective else 'OFF'} ({source}).")
        if not effective:
            self.output("Incoming DeathLinks and failed-rent DeathLinks will be ignored by the client.")
        return True


    def _cmd_state(self) -> bool:
        """Show current Luck be a Landlord AP mod state."""
        unlocks = split_unlocks(self.ctx.expand_unlocks_from_received_items())
        self.output(f"Allowed floors: {self.ctx.slot_data.get('goal_floors', [])}")
        self.output(f"Unlocked symbols/items/essences: {len(unlocks['symbols'])}/{len(unlocks['items'])}/{len(unlocks['essences'])}")
        source = "client override" if self.ctx._unlockable_chance_boost_override is not None else "slot default"
        self.output(f"Unlockable chance boost: {'ON' if self.ctx._unlockable_chance_boost_enabled() else 'OFF'} ({source})")
        return True


    def _cmd_goal(self) -> bool:
        """Goal the slot after every non-goal check is complete."""
        ok, message = self.ctx.can_manual_goal()
        if not ok:
            self.output(message)
            return False
        Utils.async_start(self.ctx.manual_goal(), name="manual Luck goal")
        self.output(message)
        return True

    def _cmd_pending(self) -> bool:
        """Show queued checks waiting to be sent on reconnect."""
        self.ctx.load_pending_checks()
        if self.ctx._pending_check_names:
            self.output("Pending checks: " + ", ".join(sorted(self.ctx._pending_check_names, key=self.ctx._natural_sort_key)))
        else:
            self.output("No pending checks queued.")
        return True

    def _cmd_restorepck(self) -> bool:
        """Restore the original Luck be a Landlord.pck from the backup now."""
        if restore_original_lbal_pck is None:
            self.output("PCK restore is not available in this client.")
            return False
        try:
            status = restore_original_lbal_pck(get_bridge_path())
            if status.get("restored"):
                self.output("Restored original Luck be a Landlord.pck.")
                return True
            self.output("Could not restore PCK: " + str(status.get("error") or "unknown error"))
            return False
        except Exception as exc:
            self.output("Could not restore PCK: " + str(exc))
            return False





class LuckContext(CommonContext):
    command_processor = LuckCommandProcessor
    game = GAME_NAME
    items_handling = 0b111

    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        self.bridge_path: Path = get_bridge_path()
        self.godot_path: Path = get_godot_userdata_path()
        self.generated_mod_path: Path = self.godot_path / "mods" / "Archipelago AP"
        self._last_generated_mod_signature: Optional[str] = None
        self._last_auto_mod_state_signature: Optional[str] = None
        self.bridge_path.mkdir(parents=True, exist_ok=True)
        self.godot_path.mkdir(parents=True, exist_ok=True)
        self.slot_data: Dict[str, Any] = {}
        self.pending_deathlinks: List[Dict[str, Any]] = []
        self.received_deathlink_counter: int = 0
        self.local_death_counter: int = 0
        self._last_sent_locations: Set[int] = set()
        self._last_received_count: int = 0
        self._run_log_offsets: Dict[str, int] = {}
        self._run_log_offsets_path = self.bridge_path / "run_log_offsets.json"
        self.load_run_log_offsets()
        self._detected_ap_check_nums: Set[int] = set()
        self._seen_game_check_nonces_v117: Set[str] = set()
        self._recent_ap_check_next_request_v117: float = 0.0
        self._last_coin_total_after_spin: Optional[int] = None
        self._last_seen_coin_total: Optional[int] = None
        self._payment_checks_sent_from_money_drop: Set[str] = set()
        self._last_seen_payment_progress: int = 0
        # V85: direct lbal_run_state.json payment tracking. This catches paid-rent
        # checks even when the run log does not contain an Add Item line.
        self._last_seen_run_state_payment_by_floor: Dict[int, int] = {}
        self._last_seen_run_state_nonce: str = ""
        # V88: prevent stale lbal_run_state/checks_to_send files from an old LBAL
        # run from being replayed immediately when the AP client connects.
        self._run_state_seen_signatures_v88: Set[str] = set()
        self._run_state_initialized_v88: bool = False
        self._client_started_at_v88: float = time.time()
        # Payment checks are sent from the Add Item screen, then locked until
        # the next gained-coins/spin line. This prevents one menu from firing
        # multiple payment checks while still making Comfy Pillow skips fast.
        self._payment_add_item_armed: bool = True
        self._pending_check_names: Set[str] = set()
        self._pending_client_goal_status: bool = False
        self._pending_check_paths = [self.bridge_path / "pending_checks.json", self.godot_path / "pending_checks.json"]
        self._deathlink_send_paths = [self.bridge_path / "deathlink_send.json", self.godot_path / "deathlink_send.json"]
        self._deathlink_receive_paths = [self.bridge_path / "deathlink_receive.json", self.godot_path / "deathlink_receive.json"]
        self._deathlink_ack_paths = [self.bridge_path / "deathlink_ack.json", self.godot_path / "deathlink_ack.json"]
        self._last_deathlink_nonce: Optional[str] = None
        self._last_local_deathlink_send_nonce: Optional[str] = None
        # V127: PCK deathlink_send.json and run-log GAME OVER fallback can both
        # fire for one failed rent. Debounce the outgoing local DeathLink path.
        self._last_local_deathlink_event_key_v127: str = ""
        self._last_local_deathlink_event_time_v127: float = 0.0
        # V74: when the game reaches normal GAME OVER without writing deathlink_send.json,
        # use the same AP-client sending path as the explicit bridge file.
        self._local_game_over_deathlink_seen_keys: Set[str] = set()
        self._local_game_over_deathlink_seen_order: List[str] = []
        self._local_death_pending_count: int = 0
        self._incoming_death_pending_count: int = 0
        self._seen_deathlink_event_keys: Set[str] = set()
        self._seen_deathlink_event_order: List[str] = []
        # V128: if LBAL dies because it received a DeathLink, do not reflect it
        # back out. If LBAL dies before the AP room is ready, retry that local
        # failed-payment DeathLink once connected.
        self._recent_received_deathlink_gameover_until_v128: float = 0.0
        self._pending_local_deathlink_cause_v128: Optional[str] = None
        # V132: send the first local failed-payment DeathLink immediately, then
        # suppress additional local DeathLink triggers for 2 seconds. This stops
        # PCK/Main/run-log duplicate attempts without delaying the first send.
        self._local_deathlink_cooldown_seconds_v132: float = 2.0
        self._local_deathlink_buffer_cause_v131: Optional[str] = None
        self._local_deathlink_buffer_deadline_v131: float = 0.0
        self._local_deathlink_buffer_task_v131: Optional[asyncio.Task] = None
        self._client_settings_path = self.bridge_path / "client_settings.json"
        self._unlockable_chance_boost_override: Optional[bool] = None
        self._unlockable_chance_boost_mode_override: Optional[str] = None
        self._rare_very_rare_pool_override: Optional[bool] = None
        self._deathlink_override: Optional[bool] = None
        self._deathlink_receive_threshold_override: Optional[int] = None
        self._deathlink_send_threshold_override: Optional[int] = None
        self._overlay_recent_client_lines_v149: List[str] = []
        self.load_pending_checks()
        # Remove stale one-shot check files from older runs before the watcher starts.
        for _stale_path in [
            self.bridge_path / "checks_to_send.json",
            self.godot_path / "checks_to_send.json",
            self.bridge_path / "deathlink_send.json",
            self.godot_path / "deathlink_send.json",
            self.bridge_path / "deathlink_receive.json",
            self.godot_path / "deathlink_receive.json",
            self.bridge_path / "deathlink_ack.json",
            self.godot_path / "deathlink_ack.json",
            self.bridge_path / "force_payment_trap_active.json",
            self.godot_path / "force_payment_trap_active.json",
        ]:
            try:
                delete_if_exists(_stale_path)
            except Exception:
                pass
        self.load_client_settings()
        self.write_state_file(connected=False)

    def load_client_settings(self) -> None:
        try:
            if not self._client_settings_path.exists():
                return
            data = json.loads(self._client_settings_path.read_text(encoding="utf-8"))
            if "unlockable_chance_boost" in data:
                value = data.get("unlockable_chance_boost")
                self._unlockable_chance_boost_override = None if value is None else bool(value)
            if "unlockable_chance_boost_mode" in data:
                value = data.get("unlockable_chance_boost_mode")
                self._unlockable_chance_boost_mode_override = None if value is None else str(value)
            if "deathlink" in data:
                value = data.get("deathlink")
                self._deathlink_override = None if value is None else bool(value)
            if "deathlink_receive_threshold" in data:
                value = data.get("deathlink_receive_threshold")
                self._deathlink_receive_threshold_override = None if value is None else max(1, min(20, int(value)))
            if "deathlink_send_threshold" in data:
                value = data.get("deathlink_send_threshold")
                self._deathlink_send_threshold_override = None if value is None else max(1, min(20, int(value)))
            if "rare_very_rare_in_game_pool" in data:
                value = data.get("rare_very_rare_in_game_pool")
                self._rare_very_rare_pool_override = None if value is None else bool(value)
        except Exception:
            self._unlockable_chance_boost_override = None
            self._unlockable_chance_boost_mode_override = None
            self._deathlink_override = None
            self._deathlink_receive_threshold_override = None
            self._deathlink_send_threshold_override = None
            self._rare_very_rare_pool_override = None

    def save_client_settings(self) -> None:
        data = {
            "unlockable_chance_boost": self._unlockable_chance_boost_override,
            "unlockable_chance_boost_mode": self._unlockable_chance_boost_mode_override,
            "deathlink": self._deathlink_override,
            "deathlink_receive_threshold": self._deathlink_receive_threshold_override,
            "deathlink_send_threshold": self._deathlink_send_threshold_override,
            "rare_very_rare_in_game_pool": self._rare_very_rare_pool_override,
        }
        atomic_write_json(self._client_settings_path, data)

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def run_gui(self):
        from kvui import GameManager

        class LuckManager(GameManager):
            # Use the normal Archipelago tab exactly like the regular text client.
            # Only add a lightweight Tracker tab.
            logging_pairs = [("Client", "Archipelago")]
            base_title = "Luck be a Landlord Client"

            def build(manager_self):
                container = super().build()
                try:
                    from kivy.clock import Clock
                    from kivy.metrics import dp, sp
                    from kivy.uix.boxlayout import BoxLayout
                    from kivy.uix.label import Label
                    from kivy.uix.scrollview import ScrollView
                    from kivy.uix.widget import Widget

                    class MissionLocationsLayout(BoxLayout):
                        def __init__(self, ctx: LuckContext, **kwargs):
                            super().__init__(orientation="vertical", padding=0, spacing=0, **kwargs)
                            self.ctx = ctx

                            self.header_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(34), padding=(dp(4), 0), spacing=dp(10))

                            def make_header_label(text="", x_hint=1, halign="left"):
                                label = Label(
                                    text=text,
                                    font_size=sp(16),
                                    halign=halign,
                                    valign="middle",
                                    color=(1, 1, 1, 1),
                                    size_hint=(x_hint, 1),
                                    shorten=True,
                                    shorten_from="right",
                                    max_lines=1,
                                )
                                label.bind(size=lambda inst, *_: setattr(inst, "text_size", (inst.width, None)))
                                return label

                            self.locations_header = make_header_label("Locations: 0/0", 1.15)
                            self.logic_header = make_header_label("In Logic: 0", 1.0)
                            self.glitched_header = make_header_label("Glitched: 0", 1.0)
                            self.hinted_header = make_header_label("Hinted: 0", 0.95)
                            self.go_header = make_header_label("Go mode: No", 1.05)
                            self.raspberry_header = make_header_label("", 1.25, "right")

                            self.header_row.add_widget(self.locations_header)
                            self.header_row.add_widget(self.logic_header)
                            self.header_row.add_widget(self.glitched_header)
                            self.header_row.add_widget(self.hinted_header)
                            self.header_row.add_widget(self.go_header)
                            self.header_row.add_widget(self.raspberry_header)
                            self.add_widget(self.header_row)

                            # Plain tracker body: no boxes/cards, just white text on the normal dark background.
                            # A spacer above the checks keeps a short list sitting at the bottom.
                            self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
                            self.content = BoxLayout(orientation="vertical", size_hint_y=None, padding=0, spacing=0)
                            self.spacer = Widget(size_hint_y=None, height=0)
                            self.list_label = Label(
                                text="",
                                font_size=sp(18),
                                halign="left",
                                valign="bottom",
                                color=(1, 1, 1, 1),
                                size_hint=(1, None),
                                height=dp(10),
                            )
                            self.list_label.bind(size=lambda *_: setattr(self.list_label, "text_size", self.list_label.size))
                            self.content.add_widget(self.spacer)
                            self.content.add_widget(self.list_label)
                            self.scroll.add_widget(self.content)
                            self.add_widget(self.scroll)

                            self.scroll.bind(size=self._layout_tracker)
                            Clock.schedule_interval(self.refresh, 1.0)
                            # Delay first refresh until Kivy has created a real widget size.
                            Clock.schedule_once(self.refresh, 0.1)
                            Clock.schedule_once(self.refresh, 0.5)

                        def _layout_tracker(self, *_args):
                            line_count = max(1, self.list_label.text.count("\n") + 1)
                            line_height = dp(27)
                            label_height = max(dp(10), line_count * line_height)
                            self.list_label.height = label_height
                            self.content.width = max(self.scroll.width, dp(100))
                            self.content.height = max(self.scroll.height, label_height)
                            self.spacer.height = max(0, self.content.height - label_height)
                            for label in (self.locations_header, self.logic_header, self.glitched_header, self.hinted_header, self.go_header, self.raspberry_header):
                                label.text_size = (label.width, None)
                            self.list_label.text_size = (self.content.width, self.list_label.height)

                        def refresh(self, *_args):
                            try:
                                total_locations = len(self.ctx.checked_locations) + len(self.ctx.missing_locations)
                                checked_locations = len(self.ctx.checked_locations)
                                sphere_locations = self.ctx.in_logic_mission_names()
                                possible_first_gets = self.ctx.possible_first_get_names()
                                in_logic_count = len(sphere_locations) + len(possible_first_gets)
                                goal_done = bool(getattr(self.ctx, "finished_game", False)) or bool(self.ctx.can_manual_goal()[0])

                                self.locations_header.text = f"Locations: {checked_locations}/{total_locations}"
                                self.logic_header.text = f"In Logic: {in_logic_count}"
                                self.glitched_header.text = "Glitched: 0"
                                self.hinted_header.text = "Hinted: 0"
                                self.go_header.text = f"Go mode: {'Yes' if goal_done else 'No'}"

                                raspberry_count, raspberry_required, raspberry_pool, raspberry_enabled = self.ctx.raspberry_tracker_counts()
                                if raspberry_enabled:
                                    self.raspberry_header.text = f"Raspberry: {raspberry_count}/{raspberry_required}"
                                else:
                                    self.raspberry_header.text = ""

                                lines = self.ctx.tracker_display_lines()

                                self.list_label.text = "\n".join(lines)
                                self._layout_tracker()
                                # Do not force scroll position every refresh; let the user scroll normally.
                            except Exception as exc:
                                logger.exception("Luck tracker refresh failed: %s", exc)

                    manager_self.add_client_tab("Tracker", MissionLocationsLayout(manager_self.ctx))
                except Exception as exc:
                    logger.exception("Could not create Luck Tracker tab: %s", exc)
                return container

        self.ui = LuckManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    def _lookup_table(self, lookup: Any) -> Dict[int, str]:
        """Convert Archipelago NameLookupDict/table objects into a normal dict.

        AP 0.6.7 uses NameLookupDict for item_names/location_names.
        It supports indexing, but not dict.get(), so the client must normalize it
        before using it like a normal mapping.
        """
        try:
            if self.game not in lookup:
                return {}
            table = lookup[self.game]
            if hasattr(table, "items"):
                return {int(code): str(name) for code, name in table.items()}
        except Exception:
            return {}
        return {}

    def location_id_to_name(self) -> Dict[int, str]:
        return self._lookup_table(self.location_names)

    def location_name_to_id(self) -> Dict[str, int]:
        return {name: loc_id for loc_id, name in self.location_id_to_name().items()}

    def item_id_to_name(self) -> Dict[int, str]:
        return self._lookup_table(self.item_names)

    def _display_item_name(self, item_name: str) -> str:
        return str(item_name)

    def expand_unlocks_from_received_items(self) -> List[str]:
        """Return actual unlock names. Bundle items are expanded using slot_data item_bundles."""
        item_lookup = self.item_id_to_name()
        bundles = self.slot_data.get("item_bundles", {}) or {}
        unlocks: List[str] = []
        for network_item in self.items_received:
            item_name = item_lookup.get(network_item.item, str(network_item.item))
            if item_name in bundles:
                unlocks.extend(bundles[item_name])
            else:
                unlocks.append(item_name)
        # Keep order but remove duplicates.
        seen = set()
        unique = []
        for name in unlocks:
            if name not in seen:
                seen.add(name)
                unique.append(name)
        return unique

    def received_items_for_state(self) -> List[Dict[str, Any]]:
        item_lookup = self.item_id_to_name()
        location_lookup = self.location_id_to_name()
        result = []
        for index, network_item in enumerate(self.items_received):
            result.append({
                "index": index,
                "item_id": network_item.item,
                "item_name": self._display_item_name(item_lookup.get(network_item.item, str(network_item.item))),
                "location_id": network_item.location,
                "location_name": location_lookup.get(network_item.location, str(network_item.location)),
                "player": network_item.player,
                "player_name": self.player_names.get(network_item.player, str(network_item.player)),
                "flags": network_item.flags,
            })
        return result

    def received_ap_effects_for_state_v139(self) -> List[Dict[str, Any]]:
        item_lookup = self.item_id_to_name()
        result: List[Dict[str, Any]] = []
        for index, network_item in enumerate(self.items_received):
            item_name = item_lookup.get(network_item.item, str(network_item.item))
            effect = AP_EFFECT_ITEM_TO_EFFECT.get(item_name)
            if not effect:
                continue
            result.append({
                "index": index,
                "item_name": item_name,
                "effect": effect,
                "source_player": network_item.player,
            })
        return result

    def ap_effect_counts_v150(self) -> Dict[str, int]:
        item_lookup = self.item_id_to_name()
        counts: Dict[str, int] = {name: 0 for name in AP_EFFECT_ITEM_TO_EFFECT}
        for network_item in self.items_received:
            item_name = item_lookup.get(network_item.item, str(network_item.item))
            if item_name in counts:
                counts[item_name] += 1
        return counts

    def ap_effect_count_v150(self, item_name: str) -> int:
        return int(self.ap_effect_counts_v150().get(item_name, 0) or 0)

    def progressive_ap_checks_received_count(self) -> int:
        item_lookup = self.item_id_to_name()
        return sum(1 for network_item in self.items_received if item_lookup.get(network_item.item, str(network_item.item)) == PROGRESSIVE_AP_CHECKS_ITEM_NAME)

    def raspberry_tracker_counts(self) -> Tuple[int, int, int, bool]:
        """Return Raspberry progress for the Tracker tab as (received, required, pool, enabled)."""
        goal_data = self.slot_data.get("raspberry_goal", {}) or {}
        if not goal_data:
            options_data = self.slot_data.get("options", {}) or {}
            pool = int(self.slot_data.get("raspberry_pool", options_data.get("raspberry_pool", 0)) or 0)
            required = int(self.slot_data.get("raspberry_required", options_data.get("raspberry_required", 0)) or 0)
            if pool > 0 and required <= 0:
                required = pool
            enabled = pool > 0 and required > 0
        else:
            enabled = bool(goal_data.get("enabled", False))
            pool = int(goal_data.get("pool", 0) or 0)
            required = int(goal_data.get("required", 0) or 0)
        if not enabled or pool <= 0 or required <= 0:
            return 0, required, pool, False

        item_lookup = self.item_id_to_name()
        count = 0
        for network_item in self.items_received:
            if item_lookup.get(network_item.item, str(network_item.item)) == "Raspberry":
                count += 1
        return count, required, pool, True

    @staticmethod
    def _natural_sort_key(name: str):
        import re
        return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", name)]

    def checked_location_names(self) -> List[str]:
        lookup = self.location_id_to_name()
        return sorted((lookup.get(loc_id, str(loc_id)) for loc_id in self.checked_locations), key=self._natural_sort_key)

    def missing_location_names(self) -> List[str]:
        lookup = self.location_id_to_name()
        return sorted((lookup.get(loc_id, str(loc_id)) for loc_id in self.missing_locations), key=self._natural_sort_key)

    def _raspberry_goal_ready(self) -> bool:
        """Return True when Raspberry goal is disabled or enough Raspberry items were received."""
        count, required, _pool, enabled = self.raspberry_tracker_counts()
        return (not enabled) or count >= required

    def _required_floor_goals_checked_or_pending(self, extra_names: Optional[Iterable[str]] = None) -> bool:
        """Return True when enough selected floor clear checks are already checked or being sent."""
        goal_floors = sorted({int(f) for f in (self.slot_data.get("goal_floors", []) or []) if 1 <= int(f) <= 20})
        if not goal_floors:
            return True
        required = int(self.slot_data.get("goal_floors_required", len(goal_floors)) or len(goal_floors))
        required = max(1, min(required, len(goal_floors)))
        cleared = set(name for name in self.checked_location_names() if name.startswith("Clear Floor "))
        if extra_names:
            cleared.update(name for name in extra_names if isinstance(name, str) and name.startswith("Clear Floor "))
        return len(cleared) >= required

    def _manual_goal_remaining_non_goal_checks(self) -> List[str]:
        """Checks that must be finished before /goal is allowed.

        Manual goal is intentionally stricter than automatic goal: the automatic
        goal only needs the selected floor clear requirement plus Raspberry, but
        /goal should only work after every real AP location has been checked.
        """
        remaining: List[str] = []
        for name in self.missing_location_names():
            # Event locations have no location id and should not appear here, but keep this safe.
            if name.endswith(" Cleared") or name.startswith("Victory Floor"):
                continue
            remaining.append(name)
        return sorted(remaining, key=self._natural_sort_key)

    def can_manual_goal(self) -> tuple[bool, str]:
        if not self.server or self.slot is None:
            return False, "Not connected to an Archipelago room yet."

        remaining = self._manual_goal_remaining_non_goal_checks()
        # If AP reports every real location checked, trust that for Go mode even
        # if missing_location_names has stale names from an old lookup table.
        try:
            all_real_ids = set(self.location_name_to_id().values())
            if all_real_ids and all_real_ids.issubset(set(self.checked_locations)):
                remaining = []
        except Exception:
            pass
        if remaining:
            preview = ", ".join(remaining[:10])
            suffix = "" if len(remaining) <= 10 else f" ... and {len(remaining) - 10} more"
            return False, f"Cannot /goal yet. Finish {len(remaining)} remaining check(s): {preview}{suffix}"

        if not self._raspberry_goal_ready():
            count, required, _pool, _enabled = self.raspberry_tracker_counts()
            return False, f"Cannot /goal yet. Raspberry is {count}/{required}."

        return True, "All checks and Raspberry requirements are complete. Sending goal now."

    async def manual_goal(self) -> None:
        """Mark CLIENT_GOAL only after Raspberry and every real check are complete."""
        ok, _message = self.can_manual_goal()
        if not ok:
            return

        await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

    def _next_unchecked_ap_check_name(self, reserved: Optional[Set[str]] = None) -> Optional[str]:
        """Return the lowest AP Check location that has not already been sent/checked.

        Before connecting, AP's location lookup can be empty. In that case still
        return AP Check 1 so the generated LBAL mod starts with AP Check symbols
        instead of empty symbols.
        """
        reserved = reserved or set()
        name_to_id = self.location_name_to_id()

        if not name_to_id:
            return "AP Check 1" if "AP Check 1" not in reserved else None

        checked_ids = set(self.checked_locations)
        sent_ids = set(getattr(self, "_last_sent_locations", set()))
        pending_ids = {
            loc_id for pending_name, loc_id in name_to_id.items()
            if pending_name in getattr(self, "_pending_check_names", set())
        }
        candidates: List[tuple[int, str]] = []

        for name, loc_id in name_to_id.items():
            match = re.fullmatch(r"AP Check (\d+)", name)
            if not match:
                continue
            if name in reserved:
                continue
            if loc_id in checked_ids or loc_id in sent_ids or loc_id in pending_ids:
                continue
            candidates.append((int(match.group(1)), name))

        if not candidates:
            return None
        candidates.sort()
        return candidates[0][1]

    def mission_location_names(self) -> List[str]:
        names = []
        unlocked_floors = set(int(f) for f in (self.unlocked_goal_floors_for_mod() or []))
        for name in self.missing_location_names():
            if name.startswith("Send: "):
                continue
            if name.endswith(" Cleared") or name.startswith("Victory Floor"):
                continue
            if name.startswith("AP Check ") or name.startswith("Payment "):
                names.append(name)
                continue
            floor_payment = re.fullmatch(r"Floor (\d+) Payment \d+", name)
            if floor_payment:
                # V82: do not show locked floor payments in the tracker fallback.
                if int(floor_payment.group(1)) in unlocked_floors:
                    names.append(name)
                continue
            if name.startswith("Clear Floor "):
                match = re.fullmatch(r"Clear Floor (\d+) Goal", name)
                if match and self._floor_goal_is_unlocked_and_ready(int(match.group(1))):
                    names.append(name)
        return sorted(names, key=self._natural_sort_key)

    def in_logic_mission_names(self) -> List[str]:
        """Return only the current AP Check group or the next Payment.

        Display order:
        - AP Check 1-10
        - Payment 1
        - AP Check 11-20
        - Payment 2
        ...
        This is only the tracker display; First-Get checks are shown separately.
        """
        missing = set(self.missing_location_names())
        checked = set(self.checked_location_names())

        # Find enabled AP Check numbers from the room.
        ap_nums: List[int] = []
        for name in missing | checked:
            match = re.fullmatch(r"AP Check (\d+)", name)
            if match:
                ap_nums.append(int(match.group(1)))
        max_ap = max(ap_nums) if ap_nums else 130

        # Progressive AP Checks: start with AP Check 1-10, then each
        # Progressive AP Checks item opens the next block of 10. The tracker
        # should not show AP Check 51-60 until 5 Progressive AP Checks are owned.
        progressive_enabled = bool((self.slot_data or {}).get("progressive_ap_checks_enabled", True))
        progressive_owned = self.progressive_ap_checks_received_count() if progressive_enabled else 999
        open_ap_groups = progressive_owned + 1

        for group_index in range(0, ((max_ap + 9) // 10)):
            start_num = group_index * 10 + 1
            end_num = min((group_index + 1) * 10, max_ap)
            group = [f"AP Check {i}" for i in range(start_num, end_num + 1)]
            current_group = [name for name in group if name in missing]
            if current_group and group_index < open_ap_groups:
                return current_group
            if current_group and group_index >= open_ap_groups:
                break

        # Payments remain their own normal progression chain.
        if self._per_floor_payment_checks_enabled():
            unlocked_floors = set(int(f) for f in (self.unlocked_goal_floors_for_mod() or []))
            active_floor = self._active_payment_floor()
            if active_floor is not None and int(active_floor) in unlocked_floors:
                for payment in range(1, 13):
                    payment_name = f"Floor {int(active_floor)} Payment {payment}"
                    if payment_name in missing:
                        return [payment_name]
            # V82: never fall back to locked floors such as Floor 5 Payment 1.
            for payment in range(1, 13):
                floor_payments = sorted(
                    [
                        name for name in missing
                        if (lambda m: bool(m and int(m.group(1)) in unlocked_floors))(re.fullmatch(rf"Floor (\d+) Payment {payment}", name))
                    ],
                    key=self._natural_sort_key,
                )
                if floor_payments:
                    return floor_payments[:10]
        else:
            for payment in range(1, 13):
                payment_name = f"Payment {payment}"
                if payment_name in missing:
                    return [payment_name]

        # After all payments are done, show ready floor goals only.
        if self._all_main_payments_done_for_goal():
            ready_goals: List[str] = []
            for name in missing:
                match = re.fullmatch(r"Clear Floor (\d+) Goal", name)
                if match and self._floor_goal_is_unlocked_and_ready(int(match.group(1))):
                    ready_goals.append(name)
            if ready_goals:
                return sorted(ready_goals, key=self._natural_sort_key)[:10]

        # Fallback: show the first remaining mission location, not every payment.
        missions = self.mission_location_names()
        return sorted(missions, key=self._natural_sort_key)[:10]

    def _send_checks_for_unlock(self, unlock: str) -> List[str]:
        """Return the Send location names that belong to one AP unlock.

        Supports the current display name format (Unlock: Name) and older
        generated seeds that used Unlock Symbol:/Unlock Item:/Unlock Essence:.
        """
        unlock_name: Optional[str] = None
        if unlock.startswith("Unlock: "):
            unlock_name = unlock.removeprefix("Unlock: ")
        elif unlock.startswith("Unlock Symbol: "):
            unlock_name = unlock.removeprefix("Unlock Symbol: ")
        elif unlock.startswith("Unlock Item: "):
            unlock_name = unlock.removeprefix("Unlock Item: ")
        elif unlock.startswith("Unlock Essence: "):
            unlock_name = unlock.removeprefix("Unlock Essence: ")

        if not unlock_name:
            return []
        names = [unlock_name]
        if unlock_name == "Matryoshka Doll":
            names = ["Matryoshka Doll", "Matryoshka Doll 2", "Matryoshka Doll 3", "Matryoshka Doll 4", "Matryoshka Doll 5"]
        return ["Send: " + name_part for name_part in names]

    def possible_first_get_names(self) -> List[str]:
        """Show Send checks that became possible from received AP unlocks."""
        if self.slot_data.get("item_bundles_enabled", False):
            return []
        missing = set(self.missing_location_names())
        sent_ids = set(getattr(self, "_last_sent_locations", set()))
        sent_names = {name for name, loc_id in self.location_name_to_id().items() if loc_id in sent_ids}
        pending_or_sent = set(self._pending_check_names) | sent_names
        possible: List[str] = []

        for unlock in self.expand_unlocks_from_received_items():
            for check_name in self._send_checks_for_unlock(unlock):
                if check_name in missing and check_name not in pending_or_sent:
                    possible.append(check_name)

        return sorted(set(possible), key=self._natural_sort_key)

    def _weight10_focus_enabled(self) -> bool:
        try:
            weight = self._unlockable_chance_weight_value()
        except Exception:
            weight = 1
        return weight >= 10 and not self.slot_data.get("item_bundles_enabled", False)

    def _has_pending_send_checks(self) -> bool:
        return any(isinstance(name, str) and name.startswith("Send: ") for name in getattr(self, "_pending_check_names", set()))

    def _focused_unlock_for_mod(self) -> Optional[str]:
        """Legacy single-target focus hook.

        The cleaner boost option now uses the same list the tracker shows as
        possible instead of forcing only the newest unlock. Keeping this method
        returning None lets AP floors keep the normal starting symbols while
        active_unlocks_for_mod() limits Add Symbol/Add Item/Add Essence rolls to
        only unfinished Send checks.
        """
        return None

    def _base_name_for_essence_rarity(self, name: str) -> str:
        """Map an Essence name back to the normal item/symbol it is based on."""
        value = str(name or "")
        if value.endswith(" Essence"):
            value = value[:-len(" Essence")]
        # Vanilla/internal naming aliases.
        aliases = {
            "5th Ace": "5th Ace",
            "Four-leaf clover": "Four-leaf clover",
            "Jack-o'-lantern": "Jack-o'-lantern",
            "Kyle the Kernite": "Kyle the Kernite",
            "The Tortoise and the Hare": "The Tortoise and the Hare",
            "Black Suits": "Black Suits",
            "Small Symbol Bomb": "Small Symbol Bomb",
            "Big Symbol Bomb": "Big Symbol Bomb",
            "Very Big Symbol Bomb": "Very Big Symbol Bomb",
            "Quantum Symbol Bomb": "Quantum Symbol Bomb",
            "Fish Tank": "Fish Tank",
        }
        return aliases.get(value, value)

    def _rarity_for_display_name(self, name: str) -> str:
        """Return AP rarity bucket for a display name.

        Essences intentionally use the rarity of their matching normal item or
        symbol. Example: Quiver Essence uses Quiver's rarity, not a separate
        Essence-list rarity.
        """
        base = self._base_name_for_essence_rarity(str(name))
        if base in VERY_RARE_SYMBOLS or base in VERY_RARE_ITEMS:
            return "very_rare"
        if base in RARE_SYMBOLS or base in RARE_ITEMS:
            return "rare"
        # Fall back to older Essence rarity lists only when there is no matching
        # normal item/symbol name.
        if base == name:
            if name in VERY_RARE_ESSENCES:
                return "very_rare"
            if name in RARE_ESSENCES:
                return "rare"
        return "normal"

    def _unlock_rarity_for_mod(self, unlock: str) -> Optional[str]:
        """Return the LBAL/AP rarity for an AP unlock display name."""
        name = None
        if unlock.startswith("Unlock: "):
            name = unlock.removeprefix("Unlock: ")
        elif unlock.startswith("Unlock Symbol: "):
            name = unlock.removeprefix("Unlock Symbol: ")
        elif unlock.startswith("Unlock Item: "):
            name = unlock.removeprefix("Unlock Item: ")
        elif unlock.startswith("Unlock Essence: "):
            name = unlock.removeprefix("Unlock Essence: ")
        if not name:
            return None
        return self._rarity_for_display_name(name)

    def _unlock_matches_boost_group(self, unlock: str, category: str, rarity: Optional[str]) -> bool:
        if self._unlock_category_for_mod(unlock) != category:
            return False
        if self._unlockable_chance_boost_mode() != "category_and_rarity":
            return True
        return self._unlock_rarity_for_mod(unlock) == rarity

    def _unlock_category_for_mod(self, unlock: str) -> Optional[str]:
        """Return symbol/item/essence for an AP unlock display name."""
        if unlock.startswith("Unlock Essence: "):
            return "essence"
        if unlock.startswith("Unlock Symbol: "):
            name = unlock.removeprefix("Unlock Symbol: ")
            return "symbol" if name == "Matryoshka Doll" or name in SYMBOLS else None
        if unlock.startswith("Unlock Item: "):
            name = unlock.removeprefix("Unlock Item: ")
            if name in NORMAL_ITEMS:
                return "item"
            if name in ESSENCES:
                return "essence"
            return None
        if not unlock.startswith("Unlock: "):
            return None
        name = unlock.removeprefix("Unlock: ")
        if name == "Matryoshka Doll" or name in SYMBOLS:
            return "symbol"
        if name in NORMAL_ITEMS:
            return "item"
        if name in ESSENCES:
            return "essence"
        return None

    def active_unlocks_for_mod(self) -> List[str]:
        """Write AP unlocks into the LBAL generated/live pool.

        regular mode:
            all received AP unlocks stay available and vanilla rarity decides
            how often each rarity appears.

        boost category/category_and_rarity mode:
            only received unlocks whose Send checks are currently possible in
            logic stay in the live pool. If a rolled rarity has no possible AP
            content, the PCK inserts the red-X missing placeholder instead of
            pulling from another rarity.
        """
        received_unlocks = [
            unlock for unlock in self.expand_unlocks_from_received_items()
            if (
                unlock.startswith("Unlock: ")
                or unlock.startswith("Unlock Symbol: ")
                or unlock.startswith("Unlock Item: ")
                or unlock.startswith("Unlock Essence: ")
            )
        ]

        # V102: The live/game pools should ALWAYS match the tracker possible list,
        # not every AP unlock that has ever been received. This is the real reason
        # locked items kept leaking: Green/Pink peppers, Lockpick, etc. were already
        # in received_unlocks, so regular mode kept them in live_pool even though
        # the tracker currently only showed AP Checks and an Essence.
        possible_checks = set(self.possible_first_get_names())
        active: List[str] = []
        for unlock in received_unlocks:
            category = self._unlock_category_for_mod(unlock)
            if category not in {"symbol", "item", "essence"}:
                continue
            send_checks = set(self._send_checks_for_unlock(unlock))
            if send_checks & possible_checks:
                active.append(unlock)

        return sorted(set(active), key=self._natural_sort_key)

    def _has_missing_ap_checks_for_mod(self) -> bool:
        """True only while the connected room still has unchecked AP Check locations.

        V82: once AP reports no AP Check names in MissingLocations, force AP Check
        out of the live/generated pool. This also prevents stale next_ap_check
        values from keeping AP Check visible after the last AP Check was sent.
        """
        name_to_id = self.location_name_to_id()
        if not name_to_id:
            return True

        missing_names = set(self.missing_location_names())
        missing_ap_checks = {name for name in missing_names if re.fullmatch(r"AP Check \d+", name)}
        if not missing_ap_checks:
            return False

        checked_ids = set(self.checked_locations) | set(getattr(self, "_last_sent_locations", set()))
        for pending_name in getattr(self, "_pending_check_names", set()):
            if isinstance(pending_name, str) and re.fullmatch(r"AP Check \d+", pending_name):
                pending_id = name_to_id.get(pending_name)
                if pending_id is not None:
                    checked_ids.add(pending_id)

        ap_check_ids = {loc_id for name, loc_id in name_to_id.items() if re.fullmatch(r"AP Check \d+", name)}
        if ap_check_ids and ap_check_ids.issubset(checked_ids):
            return False

        for name in missing_ap_checks:
            loc_id = name_to_id.get(name)
            if loc_id is None or loc_id not in checked_ids:
                return True
        return False

    def tracker_current_ap_check_names(self) -> List[str]:
        return [name for name in self.in_logic_mission_names() if name.startswith("AP Check ")]

    def tracker_display_lines(self) -> List[str]:
        # Show the current AP/payment work, then the remaining obtainable unlocks.
        # First-Get category labels are hidden; only the item/symbol/essence names show.
        sphere_lines = self.in_logic_mission_names()

        if not (self.server and self.slot is not None):
            return ["Waiting for connection..."]

        lines: List[str] = []
        if sphere_lines:
            lines.extend(sphere_lines)

        obtainable: List[str] = []
        for check_name in self.possible_first_get_names():
            if ": " in check_name:
                obtainable.append(check_name.split(": ", 1)[1])
        for name in sorted(set(obtainable), key=self._natural_sort_key):
            if name not in lines:
                lines.append(name)

        if not lines:
            lines.append("No current mission locations.")

        return lines


    def _unlockable_chance_boost_enabled(self) -> bool:
        """New cleaner slot option with optional local client override."""
        if self._unlockable_chance_boost_override is not None:
            return bool(self._unlockable_chance_boost_override)
        slot = self.slot_data or {}
        if "unlockable_chance_boost" in slot:
            return bool(slot.get("unlockable_chance_boost"))
        try:
            return int(slot.get("unlockable_chance_weight", 1) or 1) >= 10
        except Exception:
            return False

    def _unlockable_chance_boost_mode(self) -> str:
        if self._unlockable_chance_boost_mode_override:
            value = str(self._unlockable_chance_boost_mode_override).lower().replace("-", "_")
        else:
            slot = self.slot_data or {}
            value = str(
                slot.get(
                    "unlockable_chance_boost_mode",
                    (slot.get("options", {}) or {}).get("unlockable_chance_boost_mode", "regular"),
                )
            ).lower().replace("-", "_")

        if value in {"2", "rarity", "category_and_rarity", "category_rarity", "per_rarity", "rarity_and_category"}:
            return "category_and_rarity"
        if value in {"1", "category", "cat", "just_category"}:
            return "category"
        return "regular"

    def _unlockable_chance_weight_value(self) -> int:
        return 10 if (self._unlockable_chance_boost_enabled() and self._unlockable_chance_boost_mode() != "regular") else 1

    def _focus_unlock_parts(self, focused_unlock: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """Return (category, display name) for the current weight-10 focus target."""
        if not focused_unlock:
            return None, None
        if focused_unlock.startswith("Unlock: "):
            name = focused_unlock.removeprefix("Unlock: ")
            if name in SYMBOLS or name == "Matryoshka Doll":
                return "symbol", name
            if name in NORMAL_ITEMS:
                return "item", name
            if name in ESSENCES:
                return "essence", name
        if focused_unlock.startswith("Unlock Essence: "):
            return "essence", focused_unlock.removeprefix("Unlock Essence: ")
        return None, None

    def _symbol_types_for_names(self, names: Iterable[str]) -> Set[str]:
        values: Set[str] = set()
        for name in names:
            if name in AP_BYPASS_SYMBOLS:
                continue
            values.add(_display_to_lbal_type(name, "symbol"))
            values.update(SYMBOL_TYPE_ALIASES.get(name, []))
        return {
            _canonical_symbol_type_v55(v)
            for v in values
            if v and not _has_unsafe_large_numeric_suffix(v)
        }

    def _item_types_for_names(self, names: Iterable[str]) -> Set[str]:
        values: Set[str] = set()
        for name in names:
            values.add(_display_to_lbal_type(name, "item"))
            values.update(ITEM_TYPE_ALIASES.get(name, []))
        return {v for v in values if v and not _has_unsafe_large_numeric_suffix(v)}

    def _essence_types_for_names(self, names: Iterable[str]) -> Set[str]:
        values: Set[str] = set()
        for name in names:
            if not name:
                continue
            values.add(_display_to_lbal_type(name, "essence"))
            values.update(ESSENCE_TYPE_ALIASES.get(name, []))
        return {v for v in values if v and not _has_unsafe_large_numeric_suffix(v)}

    def _build_ap_floor_script(self, floor: int, symbols: List[str], items: List[str], essences: List[str], has_ap_checks: bool, all_symbols: List[str], all_items: List[str], all_essences: List[str], floor_type: Optional[str] = None, enabled: bool = True, focused_unlock: Optional[str] = None, empty_symbol_boost_pool: bool = False, empty_item_boost_pool: bool = False, empty_essence_boost_pool: bool = False, ap_check_in_symbol_pool: Optional[bool] = None) -> str:
        """Create an AP floor that keeps the normal 1-20 LBAL floor text/debuff feel."""
        internal_symbols = _filter_safe_lbal_types([_canonical_symbol_type_v55(_display_to_lbal_type(sym, "symbol")) for sym in symbols])
        for sym in symbols:
            _extend_unique(internal_symbols, SYMBOL_TYPE_ALIASES.get(sym, []))

        # Vanilla starting deck. When AP checks are finished, AP floors should
        # return to the normal LBAL start instead of leaving invalid/locked
        # placeholders that render as pink question marks.
        # V141: starting_symbol_mode decides this directly.
        # ap_checks = five AP Checks at run start.
        # starting_symbols = normal Coin/Flower/Pearl/Cherry/Cat start and AP Check appears in choices.
        starting_symbol_mode_v141 = str((self.slot_data or {}).get("starting_symbol_mode", ""))
        if starting_symbol_mode_v141 in {"ap_checks", "starting_symbols"}:
            spin_ap_checks_mode = starting_symbol_mode_v141 == "starting_symbols"
        else:
            spin_ap_checks_mode = bool((self.slot_data or {}).get("spin_ap_checks_mode", False))
        # V89: default allowed Add Symbol pool is exactly the vanilla five.
        # Do not include slot/generated starting symbols like Crab, and do not include Seed.
        vanilla_starting_symbols = ["coin", "flower", "pearl", "cherry", "cat"]
        focus_mode_active = bool(focused_unlock)
        focus_category, focus_name = self._focus_unlock_parts(focused_unlock)
        boost_pool_mode = self._unlockable_chance_boost_enabled() and self._unlockable_chance_boost_mode() != "regular"
        # V72: AP Check is still generated while AP Check locations remain, but
        # it only stays in Add Symbol rewards while there are no real AP symbol
        # targets currently possible. Once a real AP symbol can be collected,
        # the symbol pool goes back to those AP/default symbols instead of being
        # held on AP Check.
        ap_check_pool_active = has_ap_checks if ap_check_in_symbol_pool is None else bool(ap_check_in_symbol_pool)
        # Keep the proper vanilla AP starting board. Boost mode is handled by
        # active_unlocks_for_mod() limiting the included pools, not by replacing
        # the player's starting symbols with only Coins.
        focus_safe_starting_symbols = list(vanilla_starting_symbols)

        if ap_check_pool_active:
            internal_symbols.append("ap_check")
            # V76: AP Check stays available until every AP Check location is done,
            # but it must not be the only legal symbol. Keep the normal/default
            # starting symbols in the generated pool too.
            internal_symbols.extend(["ap_check"] * 9)
            if not focus_mode_active:
                for vanilla_symbol in vanilla_starting_symbols:
                    if vanilla_symbol not in internal_symbols:
                        internal_symbols.append(vanilla_symbol)
        else:
            # Make sure the vanilla starting symbols are included/unexcluded even
            # if AP has not unlocked them yet.
            for vanilla_symbol in vanilla_starting_symbols:
                if vanilla_symbol not in internal_symbols:
                    internal_symbols.append(vanilla_symbol)

        if focus_mode_active:
            for vanilla_symbol in focus_safe_starting_symbols:
                if vanilla_symbol not in internal_symbols:
                    internal_symbols.append(vanilla_symbol)

        if not internal_symbols:
            internal_symbols = list(focus_safe_starting_symbols if focus_mode_active else vanilla_starting_symbols)

        # Optional YAML weighting: repeat AP-unlocked symbols/items in the
        # included pools. Do not create fake common-rarity override Mod Data
        # entries here; those can render as pink question marks if LBAL cannot
        # inherit art/name for that generated override. 1 = normal, 10 = higher
        # chance from repeated real vanilla/AP types only.
        unlockable_chance_weight = self._unlockable_chance_weight_value()
        unlockable_chance_weight = max(1, min(10, unlockable_chance_weight))
        if unlockable_chance_weight > 1:
            weighted_symbols: List[str] = []
            for sym in symbols:
                # V77: do not extra-weight Rare/Very Rare symbols. They should stay
                # controlled by LBAL's native rarity roll; otherwise symbols like
                # Diamond can appear far too often when boost is on.
                if self._rarity_for_display_name(sym) in {"rare", "very_rare"}:
                    continue
                sym_type = _display_to_lbal_type(sym, "symbol")
                weighted_symbols.extend([sym_type] * (unlockable_chance_weight - 1))
                # Do not boost fallback aliases; invalid aliases can show as pink ? symbols.
            internal_symbols.extend(_filter_safe_lbal_types([_canonical_symbol_type_v55(sym) for sym in weighted_symbols]))

        if not focus_mode_active and boost_pool_mode and empty_symbol_boost_pool:
            # V73: when no AP symbols are currently possible, keep Add Symbol to
            # the default starting symbols only. Do NOT unlock the whole vanilla
            # or slot symbol pool here; the player asked to see only default
            # symbols plus tracker-possible symbols. Default symbols stay
            # available via allowed_symbol_types / always_allowed_symbol_types.
            pass

        # V81: save the real Add Symbol choice set BEFORE adding effect-spawned
        # helper symbols. Effect-spawned symbols may need to exist for item effects,
        # but they must not leak into normal Add Symbol choices.
        choice_symbol_types = set(internal_symbols) | set(self._symbol_types_for_names(vanilla_starting_symbols)) | {"base", "empty", "dud"}

        # Keep AP locked symbols out of the Add Symbol pool. In boost focus
        # mode, the Add Symbol pool must contain ONLY the focused new symbol.
        # Do not let the safe starting board (coin/cat/etc.) leak back into Add
        # Symbol choices; starting_symbols can still contain them, but they are
        # excluded from future rolls until focus is done.
        # Only allow the generated floor's current AP choice pool plus safe base types.
        # Effect-created symbols are kept out of excluded_symbols so items like
        # Grave Robber can create Urns mid-game, while the live PCK filter still
        # prevents those symbols from appearing as normal choices unless AP allows them.
        all_symbol_types = self._symbol_types_for_names(list(SYMBOLS) + list(all_symbols)) | set(["dice1", "dice2", "dice3", "dice4", "dice5", "d3_1", "d3_2", "d3_3"])
        effect_spawned_symbol_names = list(AP_SPAWNED_SYMBOLS) + ["Urn", "Big Urn", "Spirit"]
        effect_spawned_symbol_types = self._symbol_types_for_names(effect_spawned_symbol_names)
        # Dice roll animation needs these vanilla face texture symbols to stay available.
        # They are not valid AP choice symbols; they only support the d3/d5 animation.
        effect_spawned_symbol_types.update(DICE_FACE_TEXTURE_TYPES)
        # V90: Do not put effect-spawn helper symbols into included_symbols while
        # AP is only meant to offer the default symbols/AP Check/tracker symbols.
        # LBAL can use real effect-created symbols once their related AP content is
        # unlocked later, but they must not be selectable at Payment 0.
        if not boost_pool_mode and not ap_check_pool_active:
            for effect_symbol_type in sorted(effect_spawned_symbol_types):
                if effect_symbol_type not in internal_symbols:
                    internal_symbols.append(effect_symbol_type)

            # Dice roll animations use separate face texture IDs. Keep these on the
            # generated floor only outside the strict AP start mode.
            for dice_face_type in _dice_animation_types_v58(internal_symbols):
                if dice_face_type not in internal_symbols:
                    internal_symbols.append(dice_face_type)
        if focus_mode_active:
            allowed_symbol_types: Set[str] = {"base", "empty", "dud"}
            if focus_category == "symbol":
                if focus_name == "Matryoshka Doll":
                    allowed_symbol_types |= self._symbol_types_for_names(["Matryoshka Doll"])
                elif focus_name:
                    allowed_symbol_types |= self._symbol_types_for_names([focus_name])
            if ap_check_pool_active:
                allowed_symbol_types.add("ap_check")
        elif boost_pool_mode and empty_symbol_boost_pool:
            # V76: no tracker symbol is currently possible. Do not unlock the
            # entire vanilla symbol pool and do not make Missing AP Symbol cards.
            # Keep only default/start symbols, effect-spawn helpers, and AP Check
            # while AP Check locations remain.
            allowed_symbol_types = set(self._symbol_types_for_names(vanilla_starting_symbols)) | {"base", "empty", "dud"}
            if ap_check_pool_active:
                allowed_symbol_types.add("ap_check")
        elif boost_pool_mode:
            # Boost mode should match the Tracker possible list: normal starting
            # symbols stay usable, but old AP-unlocked symbols that already sent
            # their Send: check are excluded again.  active_unlocks_for_mod() has
            # already trimmed `symbols` to only currently possible tracker entries.
            allowed_symbol_types = set(choice_symbol_types)
            if ap_check_pool_active:
                allowed_symbol_types.add("ap_check")
        else:
            allowed_symbol_types = set(choice_symbol_types)
        if boost_pool_mode or ap_check_pool_active:
            # V118: metadata-only icons/descriptions. Include vanilla symbol IDs so
            # descriptions like Lockpick/Ritual Candle can resolve <icon_...>, but
            # still exclude locked symbols from choices. The live PCK filter and
            # excluded_symbols keep them out of Add Symbol.
            excluded_symbols = sorted(sym for sym in all_symbol_types if sym not in allowed_symbol_types)
            for metadata_symbol_type in sorted(all_symbol_types | effect_spawned_symbol_types | set(vanilla_starting_symbols) | set(DICE_FACE_TEXTURE_TYPES)):
                if metadata_symbol_type and metadata_symbol_type not in internal_symbols:
                    internal_symbols.append(metadata_symbol_type)
            # Keep duplicate AP Check weight while AP Checks are active.
            if ap_check_pool_active:
                internal_symbols.extend(["ap_check"] * 4)
        else:
            excluded_symbols = sorted(sym for sym in all_symbol_types if sym not in allowed_symbol_types and sym not in effect_spawned_symbol_types)
        if not ap_check_pool_active:
            _extend_unique(excluded_symbols, ["ap_check", "ap_check_STEAM_ID_777770", "ap_check_STEAM_ID_777770_PACK_Archipelago AP", "ap_check_STEAM_ID_777770_PACK_Archipelago_AP"])

        internal_items = _filter_safe_lbal_types([_display_to_lbal_type(item, "item") for item in items])
        for item in items:
            _extend_unique(internal_items, ITEM_TYPE_ALIASES.get(item, []))

        if self._unlockable_chance_boost_enabled():
            item_weight = self._unlockable_chance_weight_value()
            weighted_items: List[str] = []
            for item in items:
                item_type = _display_to_lbal_type(item, "item")
                weighted_items.extend([item_type] * (item_weight - 1))
                # Do not boost fallback aliases; invalid aliases can show as pink ? items.
            internal_items.extend(_filter_safe_lbal_types(weighted_items))

        # V91: do not add every vanilla item to AP floors when item randomizer is
        # off. In this AP build, Add Item should show only tracker-possible AP
        # items, or Missing AP Item if none are possible.
        if False:
            pass

        # Essence handling is deliberately different from normal items.
        # When essence_randomizer is OFF, leave essences completely vanilla.
        # Do not add every essence to included_items/excluded_items, because
        # LBAL's Essence add-item tab can collapse invalid/over-filtered essence
        # pools into repeated Pool Ball Essence choices.
        # When essence_randomizer is ON, only AP-unlocked essences are added to
        # the included pool below and locked essences are excluded.
        essence_randomizer_enabled = bool((self.slot_data or {}).get("essence_randomizer_enabled", False))
        if essence_randomizer_enabled or boost_pool_mode:
            # V80: In boost/tracker mode, do not add every vanilla essence when
            # no AP essence is possible. Missing AP Essence should handle empty
            # essence reward choices.
            essence_source = essences
            for essence in essence_source:
                _extend_unique(internal_items, sorted(self._essence_types_for_names([essence])))

        # One-per-run item rule: Comfy Pillow is allowed in the item pool normally,
        # but the live PCK filter removes it from later choices after the player
        # has collected one in the current run. It is not given as a starting item.
        ap_starting_items = []
        one_per_run_item_types = {"comfy_pillow"}

        # Same focus rule for Add Item/Add Essence: while boost focus has a
        # pending target, exclude every randomized item/essence except that one.
        # Use the full built-in constants too, because older slot_data can have
        # incomplete all_items/all_essences lists; otherwise vanilla items like
        # Pool Ball leak into the choice menu even while a new unlock is pending.
        all_item_types = self._item_types_for_names(list(NORMAL_ITEMS) + list(all_items))
        all_essence_types = self._essence_types_for_names(list(ESSENCES) + list(all_essences))
        if focus_mode_active:
            allowed_item_types: Set[str] = set()
            if focus_category == "item" and focus_name:
                allowed_item_types |= self._item_types_for_names([focus_name])
            elif focus_category == "essence" and focus_name:
                allowed_item_types |= self._essence_types_for_names([focus_name])
            excluded_pool = set(all_item_types)
            if essence_randomizer_enabled or boost_pool_mode or focus_category == "essence":
                excluded_pool |= set(all_essence_types)
            excluded_items = sorted(item for item in excluded_pool if item not in allowed_item_types)
        else:
            allowed_item_types = set(internal_items)
            excluded_pool = set(all_item_types)
            if essence_randomizer_enabled or boost_pool_mode:
                excluded_pool |= set(all_essence_types)
            excluded_items = sorted(item for item in excluded_pool if item not in allowed_item_types)

        # V118: metadata-only item descriptions/icons. Included items loads vanilla
        # names/descriptions/icon references. Excluded items and the live PCK filter
        # still prevent locked items from appearing as Add Item choices.
        for metadata_item_type in sorted(all_item_types):
            if metadata_item_type and metadata_item_type not in internal_items:
                internal_items.append(metadata_item_type)
        if essence_randomizer_enabled or boost_pool_mode:
            for metadata_essence_type in sorted(all_essence_types):
                if metadata_essence_type and metadata_essence_type not in internal_items:
                    internal_items.append(metadata_essence_type)

        floor_effects = _regular_floor_effect_values(int(floor))
        effect_counts_v150 = self.ap_effect_counts_v150()
        ap_extra_coin_bonus_v150 = 0  # V160: Main.tscn applies start buffs every run
        ap_extra_destroy_tokens_v150 = 0  # V160: Main.tscn applies start buffs every run
        ap_extra_reroll_tokens_v150 = 0  # V160: Main.tscn applies start buffs every run
        ap_extra_essence_tokens_v152 = 0  # V160: Main.tscn applies start buffs every run
        ap_big_symbol_bombs_v150 = 0  # V160: Main.tscn applies Choice of Symbols every run
        # V151: Dud trap is immediate/current-run only, not a permanent start-of-run modifier.
        ap_dud_traps_v150 = int(effect_counts_v150.get("Trap: Add Dud Symbol", 0) or 0)
        starting_duds = ["dud"] * int(floor_effects.get("starting_duds", 0))

        # Some base floors start with Dud/X symbols. On a generated AP floor, LBAL
        # can show those as question marks if dud is only present in starting_symbols
        # but not in the floor's included_symbols. Include it explicitly so the
        # base-game X art is used.
        if starting_duds and "dud" not in internal_symbols:
            internal_symbols.append("dud")
        if ap_big_symbol_bombs_v150 > 0:
            for _ap_bomb_idx_v150 in range(ap_big_symbol_bombs_v150):
                ap_starting_items.append("symbol_bomb_big")
            _extend_unique(internal_items, ["symbol_bomb_big"])

        if focus_mode_active:
            starting = list(vanilla_starting_symbols) + starting_duds
        elif has_ap_checks and not spin_ap_checks_mode:
            starting = ["ap_check", "ap_check", "ap_check", "ap_check", "ap_check"] + starting_duds
        else:
            # AP checks are complete, or AP Check count is low and checks are
            # meant to appear during spins: explicitly use the safe base board.
            starting = list(vanilla_starting_symbols) + starting_duds

        floor_type = floor_type or f"archipelago_ap_floor_{int(floor)}"
        floor_text = _regular_floor_text(int(floor))
        if not enabled:
            floor_text = "<icon_dud> This floor is not selected in this Archipelago seed. It will not give AP Checks or AP unlock items.\n\n" + floor_text
        rr, rm, re_ = _regular_floor_tokens(int(floor))
        rr += ap_extra_reroll_tokens_v150
        rm += ap_extra_destroy_tokens_v150
        re_ += ap_extra_essence_tokens_v152
        # Keep this as a modded AP floor, but show the same normal floor modifier text.
        # AP gameplay still uses the AP Check pool; the normal-floor text is for selecting 1-20.
        return "\n".join([
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            '\tmod_type = "apartment_floor"',
            f'\ttype = "{floor_type}"',
            '\tdisplay_name = "Archipelago AP"',
            '\tlocalized_names = {}',
            '\tinherit_description = false',
            f'\tdescription = {json.dumps(floor_text)}',
            f'\ttext = {json.dumps(floor_text)}',
            f'\tlocalized_descriptions = {{"en": {json.dumps(floor_text)}}}',
            f'\tlocalized_text = {{"en": {json.dumps(floor_text)}}}',
            '\tauthor_id = "777770"',
            f'\tfloor_num = {int(floor)}',
            '\tlocked = false',
            '\thas_bossfight = true',
            f'\tlandlord_hp = {int(floor_effects.get("landlord_hp", 750))}',
            f'\tlandlord_max_hp = {int(floor_effects.get("landlord_max_hp", 750))}',
            f'\tfine_print_multiplier = {int(floor_effects.get("fine_print_multiplier", 1))}',
            f'\tdud_timer = {int(floor_effects.get("dud_timer", 0))}',
            f'\tstarting_coins = {1 + int(ap_extra_coin_bonus_v150)}',
            '\trent_payments = 12',
            f'\tcomrade_reroll_tokens = {rr}',
            f'\tcomrade_removal_tokens = {rm}',
            f'\tcomrade_essence_tokens = {re_}',
            *( [f'\tstarting_symbols = {_gd_array(starting)}'] if starting is not None else [] ),
            f'\tstarting_items = {_gd_array(ap_starting_items)}',
            '\tsymbol_packs = []',
            f'\tincluded_symbols = {_gd_array(internal_symbols)}',
            f'\texcluded_symbols = {_gd_array(excluded_symbols)}',
            '\titem_packs = []',
            f'\tincluded_items = {_gd_array(internal_items)}',
            f'\texcluded_items = {_gd_array(excluded_items)}',
            '\temail_packs = ["base", "self"]',
            '\tincluded_emails = []',
            '\texcluded_emails = []',
            '\trent_values = ["base"]',
            '',
        ])

    def _build_rarity_override_script(self, mod_type: str, type_name: str) -> str:
        """Create a tiny override so AP-unlocked content is easier to find in-game.

        The earlier weighting only repeated entries in included_symbols/items, but
        LBAL largely uses the symbol/item rarity when rolling Add Symbol/Add Item
        choices.  This override keeps the vanilla art/effects/description while
        forcing the generated AP-unlocked entry to common rarity.
        """
        return "\n".join([
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            f'\tmod_type = {json.dumps(mod_type)}',
            f'\ttype = {json.dumps(type_name)}',
            '\tauthor_id = "777770"',
            '\tinherit_effects = true',
            '\tinherit_art = true',
            '\tinherit_groups = true',
            '\tinherit_description = true',
            '\tinherit_description = true',
            '\trarity = "common"',
            '',
        ])

    def _build_easy_content_script(self, entry: Dict[str, Any]) -> str:
        """Build a simple built-in content-pack symbol/item/essence script.

        This is deliberately for easy support only: name, type/id, rarity, value,
        groups, description, and optional static art copied into the generated mod.
        Complex custom GDScript effects still need a proper LBAL mod.
        """
        kind = str(entry.get("kind", "item"))
        mod_type = "symbol" if kind == "symbol" else "item"
        type_id = str(entry.get("id") or entry.get("type"))
        name = str(entry.get("name") or type_id)
        rarity = str(entry.get("rarity") or ("essence" if kind == "essence" else "common"))
        desc = str(entry.get("description") or (f"AP content-pack {name}."))
        value = int(entry.get("value", 0) or 0)
        groups = entry.get("groups", [])
        if not isinstance(groups, list):
            groups = []
        lines = [
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            f'\tmod_type = {json.dumps(mod_type)}',
            f'\ttype = {json.dumps(type_id)}',
            f'\tdisplay_name = {json.dumps(name)}',
            '\tauthor_id = "777770"',
            '\tinherit_effects = false',
            '\tinherit_art = false',
            '\tinherit_groups = false',
            '\tinherit_description = false',
            f'\tdescription = {json.dumps(desc)}',
            '\tlocalized_names = {}',
            '\tlocalized_descriptions = {}',
            f'\trarity = {json.dumps(rarity)}',
            f'\tgroups = {_gd_array([str(g) for g in groups])}',
        ]
        if mod_type == "symbol":
            lines.extend([
                f'\tvalue = {value}',
                f'\tvalue_text = {{"value": {json.dumps(str(value))}}}',
            ])
        else:
            lines.extend(['\tvalues = []'])
        lines.append('')
        return "\n".join(lines)

    def _write_easy_content_pack_scripts(self, scripts_path: Path, art_path: Path) -> None:
        entries = list(EASY_CONTENT.get("symbols", [])) + list(EASY_CONTENT.get("items", [])) + list(EASY_CONTENT.get("essences", []))
        if not entries:
            return
        for old in scripts_path.glob("ap_easy_*.gd"):
            try:
                old.unlink()
            except OSError:
                pass
        for entry in entries:
            type_id = str(entry.get("id") or entry.get("type") or "").strip()
            if not type_id or _has_unsafe_large_numeric_suffix(type_id):
                continue
            (scripts_path / f"ap_easy_{type_id}.gd").write_text(self._build_easy_content_script(entry), encoding="utf-8")
            texture = str(entry.get("texture") or "").strip()
            if texture:
                # Art files are expected under luck_be_a_landlord/mod_content/art/ inside the APWorld.
                for pkg_name in (f"mod_content/art/{texture}", f"mod_content/easy_packs/{texture}"):
                    try:
                        data = pkgutil.get_data(__package__ or "luck_be_a_landlord", pkg_name)
                    except Exception:
                        data = None
                    if data:
                        try:
                            (art_path / f"{type_id}.png").write_bytes(data)
                        except Exception:
                            pass
                        break

    def _write_missing_fallback_art_only(self, art_path: Path) -> None:
        """Only replace the missing/question-mark fallback image files with the uploaded red-X image.

        This does NOT add every symbol/item/essence as a mod script.
        It only writes art files for the generic missing fallback names.
        """
        try:
            image_bytes = pkgutil.get_data(__package__ or "luck_be_a_landlord", "mod_content/art/ap_missing_placeholder.png")
        except Exception:
            image_bytes = None
        if not image_bytes:
            return

        missing_names = [
            "missing",
            "item_missing",
            "symbol_missing",
            "missing_item",
            "missing_symbol",
            "question_mark",
            "unknown",
            "ap_missing",
            "ap_locked",
            "locked",
        ]

        for name in missing_names:
            for art_name in (
                f"{name}.png",
                f"{name}_STEAM_ID_777770.png",
                f"{name}_STEAM_ID_777770_PACK_Archipelago AP.png",
                f"{name}_STEAM_ID_777770_PACK_Archipelago_AP.png",
            ):
                try:
                    (art_path / art_name).write_bytes(image_bytes)
                except Exception:
                    pass

    def _build_icon_only_symbol_script(self, type_name: str, display_name: str) -> str:
        """Register a vanilla symbol icon for descriptions without adding it to the AP floor pool."""
        return "\n".join([
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            '\tmod_type = "symbol"',
            f'\ttype = {json.dumps(type_name)}',
            f'\tdisplay_name = {json.dumps(display_name)}',
            '\tauthor_id = "777770"',
            '\tinherit_effects = true',
            '\tinherit_art = true',
            '\tinherit_groups = true',
            '\tinherit_description = true',
            '\trarity = "none"',
            '',
        ])

    def _build_icon_only_item_script(self, type_name: str, display_name: str, essence: bool = False) -> str:
        """Register a vanilla item/essence icon for inline descriptions without making it a reward target."""
        rarity = "essence" if essence else "none"
        groups = '["essence"]' if essence else '[]'
        return "\n".join([
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            '\tmod_type = "item"',
            f'\ttype = {json.dumps(type_name)}',
            f'\tdisplay_name = {json.dumps(display_name)}',
            '\tauthor_id = "777770"',
            '\tinherit_effects = true',
            '\tinherit_art = true',
            '\tinherit_groups = true',
            '\tinherit_description = true',
            f'\trarity = {json.dumps(rarity)}',
            f'\tgroups = {groups}',
            '',
        ])

    def _write_item_description_icon_scripts(self, scripts_path: Path) -> None:
        """Write curated icon-only item/essence scripts for inline descriptions.

        V125: keep item description icons, but do not generate unsafe large
        numeric/workshop-style IDs.
        """
        for old in list(scripts_path.glob("ap_icon_only_*.gd")):
            try:
                old.unlink()
            except OSError:
                pass
        item_names: Dict[str, str] = {}
        for display_name in list(NORMAL_ITEMS):
            for type_name in self._item_types_for_names([display_name]):
                if type_name:
                    item_names.setdefault(type_name, display_name)
        # Critical aliases used by vanilla text / old AP mappings.
        for type_name, display_name in {
            "red_suits": "Red Suits",
            "blue_suits": "Black Suits",
            "black_suits": "Black Suits",
            "red_suit": "Red Suits",
            "black_suit": "Black Suits",
        }.items():
            item_names.setdefault(type_name, display_name)

        essence_names: Dict[str, str] = {}
        for display_name in list(ESSENCES):
            for type_name in self._essence_types_for_names([display_name]):
                if type_name:
                    essence_names.setdefault(type_name, display_name)
        for type_name, display_name in {
            "red_suits_essence": "Red Suits Essence",
            "blue_suits_essence": "Black Suits Essence",
            "black_suits_essence": "Black Suits Essence",
        }.items():
            essence_names.setdefault(type_name, display_name)

        for type_name, display_name in sorted(item_names.items()):
            if not type_name or _has_unsafe_large_numeric_suffix(type_name):
                continue
            try:
                (scripts_path / f"ap_icon_only_item_{type_name}.gd").write_text(
                    self._build_icon_only_item_script(type_name, display_name, False),
                    encoding="utf-8",
                )
            except Exception:
                pass

        for type_name, display_name in sorted(essence_names.items()):
            if not type_name or _has_unsafe_large_numeric_suffix(type_name):
                continue
            try:
                (scripts_path / f"ap_icon_only_essence_{type_name}.gd").write_text(
                    self._build_icon_only_item_script(type_name, display_name, True),
                    encoding="utf-8",
                )
            except Exception:
                pass

    def _write_suit_description_icon_scripts(self, scripts_path: Path) -> None:
        """Write curated icon-only scripts for inline description icons.

        V125: v123 wrote icon-only scripts for every vanilla symbol. On some
        Steam/Godot builds that can touch workshop-style IDs such as
        *_2895537308 and trigger String.to_int overflow spam. Keep the metadata
        layer, but only register the symbols commonly referenced by descriptions.
        These are icon/description loaders only; AP choice pools are still gated
        by the live PCK filter.
        """
        icon_names: Dict[str, str] = {
            "clubs": "Clubs", "club": "Clubs", "spades": "Spades", "spade": "Spades",
            "hearts": "Hearts", "heart": "Hearts", "diamonds": "Diamonds", "diamond": "Diamonds",
            "ore": "Ore", "big_ore": "Big Ore", "void_stone": "Void Stone", "void_creature": "Void Creature",
            "toddler": "Toddler", "dog": "Dog", "wolf": "Wolf", "bird": "Bird", "birdhouse": "Birdhouse",
            "egg": "Egg", "goose": "Goose", "chick": "Chick", "chicken": "Chicken",
            "bee": "Bee", "honey": "Honey", "flower": "Flower", "rain": "Rain", "sun": "Sun",
            "seed": "Seed", "banana": "Banana", "banana_peel": "Banana Peel", "monkey": "Monkey",
            "mouse": "Mouse", "ninja": "Ninja", "cat": "Cat", "milk": "Milk", "fish": "Fish",
            "goldfish": "Goldfish", "dwarf": "Dwarf", "beer": "Beer", "wine": "Wine",
            "hooligan": "Hooligan", "urn": "Urn", "big_urn": "Big Urn", "spirit": "Spirit",
            "bounty_hunter": "Bounty Hunter", "target": "Target", "key": "Key", "lockbox": "Lockbox",
            "safe": "Safe", "treasure_chest": "Treasure Chest", "mega_chest": "Mega Chest",
            "pirate": "Pirate", "anchor": "Anchor", "diver": "Diver", "miner": "Miner",
            "geologist": "Geologist", "archaeologist": "Geologist", "pearl": "Pearl",
            "shiny_pebble": "Shiny Pebble", "chemical_seven": "Chemical Seven", "lucky_seven": "Lucky Seven",
            "coin": "Coin", "rabbit": "Rabbit", "rabbit_fluff": "Rabbit Fluff", "cultist": "Cultist",
            "witch": "Witch", "hex_of_tedium": "Hex of Tedium", "hex_of_destruction": "Hex of Destruction",
            "red_suits": "Red Suits", "blue_suits": "Black Suits", "black_suits": "Black Suits",
        }
        for type_name, display_name in sorted(icon_names.items()):
            if not type_name or _has_unsafe_large_numeric_suffix(type_name):
                continue
            try:
                (scripts_path / f"ap_icon_only_symbol_{type_name}.gd").write_text(
                    self._build_icon_only_symbol_script(type_name, display_name), encoding="utf-8"
                )
            except Exception:
                pass

    def _build_generic_missing_description_script(self, mod_type: str, type_name: str, display_name: str, description: str) -> str:
        """Register a description for the generic missing/? placeholder only."""
        return "\n".join([
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            f'\tmod_type = {json.dumps(mod_type)}',
            f'\ttype = {json.dumps(type_name)}',
            f'\tdisplay_name = {json.dumps(display_name)}',
            '\tauthor_id = "777770"',
            '\tinherit_effects = true',
            '\tinherit_art = true',
            '\tinherit_groups = true',
            '\tinherit_description = false',
            '\tmodded = true',
            f'\tdescription = {json.dumps(description)}',
            f'\ttext = {json.dumps(description)}',
            f'\tlocalized_names = {{"en": {json.dumps(display_name)}}}',
            f'\tlocalized_descriptions = {{"en": {json.dumps(description)}}}',
            f'\tlocalized_text = {{"en": {json.dumps(description)}}}',
            '\trarity = "none"',
            '',
        ])

    def _write_generic_missing_description_scripts(self, scripts_path: Path) -> None:
        """Give the generic red-X missing placeholder readable text.

        This only writes a few generic fallback scripts. It does not add all
        game symbols/items/essences to the mod.
        """
        generic = {
            "missing": ("symbol", "Missing AP Content", "This icon is locked or missing because Archipelago has not allowed that content yet."),
            "question_mark": ("symbol", "Missing AP Content", "This icon is locked or missing because Archipelago has not allowed that content yet."),
            "unknown": ("symbol", "Missing AP Content", "This icon is locked or missing because Archipelago has not allowed that content yet."),
            "symbol_missing": ("symbol", "Missing AP Symbol", "This symbol is locked by Archipelago. Find its AP unlock before it can appear normally."),
            "missing_symbol": ("symbol", "Missing AP Symbol", "This symbol is locked by Archipelago. Find its AP unlock before it can appear normally."),
            "item_missing": ("item", "Missing AP Item", "This item or essence is locked by Archipelago. Find its AP unlock before it can appear normally."),
            "missing_item": ("item", "Missing AP Item", "This item or essence is locked by Archipelago. Find its AP unlock before it can appear normally."),
            "ap_missing": ("symbol", "Missing AP Content", "This icon is locked or missing because Archipelago has not allowed that content yet."),
            "ap_locked": ("symbol", "Locked AP Content", "This content is locked by Archipelago. Find its AP unlock before it can appear normally."),
            "locked": ("symbol", "Locked AP Content", "This content is locked by Archipelago. Find its AP unlock before it can appear normally."),
        }
        for type_name, (mod_type, display_name, description) in generic.items():
            try:
                (scripts_path / f"ap_missing_desc_{mod_type}_{type_name}.gd").write_text(
                    self._build_generic_missing_description_script(mod_type, type_name, display_name, description),
                    encoding="utf-8",
                )
            except Exception:
                pass

    def _build_missing_choice_placeholder_script(self, mod_type: str, type_name: str, display_name: str, rarity: str, description: str) -> str:
        """Small red-X placeholder used only when the rolled rarity has no valid AP choices."""
        return "\n".join([
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            f'\tmod_type = {json.dumps(mod_type)}',
            f'\ttype = {json.dumps(type_name)}',
            f'\tdisplay_name = {json.dumps(display_name)}',
            '\tauthor_id = "777770"',
            '\tmodded = true',
            '\tinherit_effects = false',
            '\tinherit_art = false',
            '\tinherit_groups = false',
            '\tinherit_description = false',
            f'\tdescription = {json.dumps(description)}',
            f'\ttext = {json.dumps(description)}',
            f'\tlocalized_names = {{"en": {json.dumps(display_name)}}}',
            f'\tlocalized_descriptions = {{"en": {json.dumps(description)}}}',
            f'\tlocalized_text = {{"en": {json.dumps(description)}}}',
            f'\trarity = {json.dumps(rarity)}',
            '\tgroups = []',
            '\tvalues = []',
            '\tvalue = 0',
            '\tvalue_text = {"value": "0"}',
            '\teffects = []',
            '\tsfx = []',
            '\tcan_be_destroyed_before_rent = false',
            '\tmanually_destroyable = false',
            '',
        ])

    def _write_missing_choice_placeholder_scripts(self, scripts_path: Path, art_path: Path) -> None:
        """Write red-X missing placeholders for Items and Essences only.

        V79: Missing AP Symbol should never appear as an Add Symbol card. Symbols
        fall back to default/start symbols plus AP Check/tracker-unlocked symbols.
        Item and Essence placeholders still exist for empty AP reward rarities.
        """
        try:
            image_bytes = pkgutil.get_data(__package__ or "luck_be_a_landlord", "mod_content/art/ap_missing_placeholder.png")
        except Exception:
            image_bytes = None

        # Clean up symbol placeholder scripts from older builds so stale files in
        # the generated mod folder cannot keep adding Missing AP Symbol cards.
        for rarity in ["common", "uncommon", "rare", "very_rare"]:
            sym_type = f"ap_missing_symbol_{rarity}"
            try:
                old_script = scripts_path / f"{sym_type}.gd"
                if old_script.exists():
                    old_script.unlink()
            except Exception:
                pass

        rarities = ["common", "uncommon", "rare", "very_rare"]
        for rarity in rarities:
            # V107: create three distinct Missing AP Item IDs per rarity so LBAL
            # cannot erase one placeholder and then refill remaining cards with vanilla items.
            for missing_index in range(1, 4):
                item_type = f"ap_missing_item_{rarity}_{missing_index}"
                try:
                    (scripts_path / f"{item_type}.gd").write_text(
                        self._build_missing_choice_placeholder_script(
                            "item",
                            item_type,
                            "Missing AP Item",
                            rarity,
                            "The rolled rarity has no possible AP item yet. Find more AP unlocks to fill this rarity.",
                        ),
                        encoding="utf-8",
                    )
                    if image_bytes:
                        for art_name in (
                            f"{item_type}.png",
                            f"{item_type}_STEAM_ID_777770.png",
                            f"{item_type}_STEAM_ID_777770_PACK_Archipelago AP.png",
                            f"{item_type}_STEAM_ID_777770_PACK_Archipelago_AP.png",
                        ):
                            try:
                                (art_path / art_name).write_bytes(image_bytes)
                            except Exception:
                                pass
                except Exception:
                    pass
            item_type = f"ap_missing_item_{rarity}"
            try:
                (scripts_path / f"{item_type}.gd").write_text(
                    self._build_missing_choice_placeholder_script(
                        "item",
                        item_type,
                        "Missing AP Item",
                        rarity,
                        "The rolled rarity has no possible AP item yet. Find more AP unlocks to fill this rarity.",
                    ),
                    encoding="utf-8",
                )
                if image_bytes:
                    for art_name in (
                        f"{item_type}.png",
                        f"{item_type}_STEAM_ID_777770.png",
                        f"{item_type}_STEAM_ID_777770_PACK_Archipelago AP.png",
                        f"{item_type}_STEAM_ID_777770_PACK_Archipelago_AP.png",
                    ):
                        try:
                            (art_path / art_name).write_bytes(image_bytes)
                        except Exception:
                            pass
            except Exception:
                pass

        # Essence screens use the item renderer/rules.
        essence_type = "ap_missing_item_essence"
        try:
            (scripts_path / f"{essence_type}.gd").write_text(
                self._build_missing_choice_placeholder_script(
                    "item",
                    essence_type,
                    "Missing AP Essence",
                    "essence",
                    "This Essence reward has no possible AP essence yet. Find more AP unlocks to fill this reward.",
                ),
                encoding="utf-8",
            )
            if image_bytes:
                for art_name in (
                    f"{essence_type}.png",
                    f"{essence_type}_STEAM_ID_777770.png",
                    f"{essence_type}_STEAM_ID_777770_PACK_Archipelago AP.png",
                    f"{essence_type}_STEAM_ID_777770_PACK_Archipelago_AP.png",
                ):
                    try:
                        (art_path / art_name).write_bytes(image_bytes)
                    except Exception:
                        pass
        except Exception:
            pass

    def _build_ap_check_symbol_script(self) -> str:
        """Create the single AP Check symbol.

        It displays as AP Check, uses ap_check.png art, gives 3 coins from
        its normal value, then destroys itself. The client only counts the
        self-destroy effect log line, so each symbol should send one check.
        """
        return "\n".join([
            'extends "res://Mod Data.gd"',
            '',
            'func _init():',
            '\tmod_type = "symbol"',
            '\ttype = "ap_check"',
            '\tdisplay_name = "AP Check"',
            '\tauthor_id = "777770"',
            '\tinherit_effects = false',
            '\tinherit_art = false',
            '\tinherit_groups = false',
            '\tinherit_description = false',
            '\tvalue = 3',
            '\tvalue_text = {"value": "3"}',
            '\tdescription = "Gives <icon_coin>3, then destroys itself and sends the next <color_800080>AP Check<end>."',
            '\tlocalized_names = {}',
            '\tlocalized_descriptions = {}',
            '\tvalues = []',
            '\trarity = "common"',
            '\tgroups = []',
            '\tsfx = []',
            '\tcan_be_destroyed_before_rent = true',
            '\tmanually_destroyable = false',
            '\teffects = [',
            '\t{"effect_type": "self", "value_to_change": "destroyed", "diff": true, "anim": "shake", "anim_targets": "self"}',
            '\t]',
            '',
        ])

    def _current_ap_check_nums_for_mod(self) -> List[int]:
        missing = set(self.missing_location_names())
        nums: List[int] = []
        for name in missing:
            match = re.fullmatch(r"AP Check (\d+)", name)
            if match:
                nums.append(int(match.group(1)))
        if not nums:
            # Before connecting / before missing locations are known, generate a
            # useful starter set so the floor is not empty.
            nums = list(range(1, 11))
        return sorted(set(nums))

    def _floor_unlock_mode_from_slot_v67(self) -> str:
        slot = self.slot_data or {}
        options = slot.get("options", {}) or {}
        value = slot.get("floor_unlock_mode", options.get("floor_unlock_mode", "start_with_all"))
        if isinstance(value, str):
            value = value.strip().lower()
            if value in {"unlock_through_items", "unlock", "items", "1", "true", "on"}:
                return "unlock_through_items"
            return "start_with_all"
        try:
            return "unlock_through_items" if int(value) == 1 else "start_with_all"
        except Exception:
            return "start_with_all"

    def unlocked_goal_floors_for_mod(self) -> List[int]:
        goal_floors = [int(f) for f in (self.slot_data.get("goal_floors", []) or [1])]
        if self._floor_unlock_mode_from_slot_v67() != "unlock_through_items":
            return goal_floors
        if not goal_floors:
            return [1]
        unlocked = {goal_floors[0]}
        for entry in self.received_items_for_state():
            name = str(entry.get("item_name", ""))
            m = re.fullmatch(r"Unlock Floor (\d+)", name)
            if m:
                unlocked.add(int(m.group(1)))
        return [floor for floor in goal_floors if floor in unlocked]


    def _rare_very_rare_pool_enabled(self) -> bool:
        if self._rare_very_rare_pool_override is not None:
            return bool(self._rare_very_rare_pool_override)
        slot = self.slot_data or {}
        if "rare_very_rare_in_game_pool_enabled" in slot:
            return bool(slot.get("rare_very_rare_in_game_pool_enabled"))
        pool = slot.get("vanilla_rarity_pool")
        if isinstance(pool, dict) and "enabled" in pool:
            return bool(pool.get("enabled"))
        options = slot.get("options", {}) or {}
        if "rare_very_rare_in_game_pool" in options:
            try:
                return int(options.get("rare_very_rare_in_game_pool")) == 1
            except Exception:
                return bool(options.get("rare_very_rare_in_game_pool"))
        return True

    def _vanilla_rarity_pool_from_slot(self) -> Dict[str, List[str]]:
        """Rare/Very Rare content removed from AP checks/items but optionally kept in LBAL pool.

        Essences use the rarity of their matching regular item/symbol so
        Quiver Essence follows Quiver, Black Suits Essence follows Black Suits,
        etc.
        """
        if not self._rare_very_rare_pool_enabled():
            return {"symbols": [], "items": [], "essences": []}

        slot = self.slot_data or {}
        rare_on = bool(slot.get("rare_checks_enabled", True))
        very_rare_on = bool(slot.get("very_rare_checks_enabled", True))

        rare_essences_by_base = [
            essence for essence in ESSENCES
            if self._rarity_for_display_name(essence) == "rare"
        ]
        very_rare_essences_by_base = [
            essence for essence in ESSENCES
            if self._rarity_for_display_name(essence) == "very_rare"
        ]

        rebuilt = {
            "symbols": sorted(set(([] if rare_on else list(RARE_SYMBOLS)) + ([] if very_rare_on else list(VERY_RARE_SYMBOLS)))),
            "items": sorted(set(([] if rare_on else list(RARE_ITEMS)) + ([] if very_rare_on else list(VERY_RARE_ITEMS)))),
            "essences": sorted(set(
                ([] if rare_on else rare_essences_by_base)
                + ([] if very_rare_on else very_rare_essences_by_base)
            )),
        }

        pool = slot.get("vanilla_rarity_pool")
        if isinstance(pool, dict):
            for key in ("symbols", "items", "essences"):
                rebuilt[key] = sorted(
                    set(rebuilt[key] + [str(x) for x in pool.get(key, []) if str(x)]),
                    key=self._natural_sort_key,
                )

        return rebuilt

    def _add_vanilla_rarity_pool(self, split: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Add Rare/Very Rare in-game-only content once, without weighting it.

        This keeps rare_checks/very_rare_checks off content in the LBAL pool
        without making it AP checks/items and without boosting its chance.
        Actual rarity still comes from the vanilla symbol/item data.
        """
        pool = self._vanilla_rarity_pool_from_slot()
        return {
            "symbols": sorted(set(list(split.get("symbols", [])) + list(pool.get("symbols", []))), key=self._natural_sort_key),
            "items": sorted(set(list(split.get("items", [])) + list(pool.get("items", []))), key=self._natural_sort_key),
            "essences": sorted(set(list(split.get("essences", [])) + list(pool.get("essences", []))), key=self._natural_sort_key),
            "other": sorted(set(split.get("other", [])), key=self._natural_sort_key),
        }

    def write_generated_lbal_mod(self, force: bool = False) -> None:
        """Generate a normal LBAL user mod folder from AP state.

        This avoids replacing the Steam .pck. The generated mod uses only supported
        LBAL Mod Data assignments, so it should load through the vanilla mod system.

        Live update mode: the AP client automatically refreshes this mod folder
        whenever AP unlocks/checks change. AP Check remains available while AP Check locations are missing,
        but V72 releases the Add Symbol pool back to real AP symbols when one is possible. LBAL may still cache the currently
        opened Add Symbol menu; close/reopen the choice screen or start a new AP
        floor if the game does not re-read mod data during the current run.
        """
        try:
            ensure_ap_check_art_files()
            expanded_unlocks = self.active_unlocks_for_mod()
            split = split_unlocks(expanded_unlocks)
            # V109: live symbol fallback needs generated scripts/icons/database entries.
            # If there are no symbol Send checks in the tracker, include already-
            # received AP symbols in the generated floor. Items/essences remain
            # tracker-possible only and are NOT added here.
            if len(split.get("symbols", [])) == 0:
                received_symbol_unlocks = []
                for unlock in self.expand_unlocks_from_received_items():
                    if (
                        isinstance(unlock, str)
                        and (
                            unlock.startswith("Unlock: ")
                            or unlock.startswith("Unlock Symbol: ")
                            or unlock.startswith("Unlock Item: ")
                        )
                        and self._unlock_category_for_mod(unlock) == "symbol"
                    ):
                        received_symbol_unlocks.append(unlock)
                if received_symbol_unlocks:
                    expanded_unlocks = sorted(set(list(expanded_unlocks) + received_symbol_unlocks), key=self._natural_sort_key)
                    split = split_unlocks(expanded_unlocks)
            # V81/V109: strict AP pools. Only symbols get the received fallback above.
            split_with_vanilla = split
            boost_pool_mode = self._unlockable_chance_boost_enabled() and self._unlockable_chance_boost_mode() != "regular"
            empty_symbol_boost_pool = boost_pool_mode and len(split.get("symbols", [])) == 0
            empty_item_boost_pool = boost_pool_mode and len(split.get("items", [])) == 0
            empty_essence_boost_pool = boost_pool_mode and len(split.get("essences", [])) == 0
            # Generate only the AP floors chosen in the seed. This keeps the AP
            # floor screen to one page for seeds such as 1, 10, and 20, instead
            # of making pages full of disabled floors.
            goal_floors = sorted({int(f) for f in (self.slot_data.get("goal_floors", []) or []) if 1 <= int(f) <= 20})
            floors = self.unlocked_goal_floors_for_mod() or [goal_floors[0] if goal_floors else 1]
            # Keep the AP Check symbol available only while the connected room
            # still has unchecked AP Check locations. This stops the pink AP Check
            # symbol from staying in the Add Symbol pool after every AP Check is done,
            # including low-filler/spin-check mode.
            has_ap_checks = self._has_missing_ap_checks_for_mod()
            # V72: if a real AP Symbol location is possible, stop weighting AP Check
            # in Add Symbol rewards so the real symbol/default pool can appear.
            # V75: keep AP Check in Add Symbol while AP Check checks remain,
            # even when a real tracker symbol is also possible.
            ap_check_in_symbol_pool = has_ap_checks
            next_ap_check = self._next_unchecked_ap_check_name() if has_ap_checks else None
            focused_unlock = None
            signature = json.dumps({"floors": floors, "goal_floors": goal_floors, "symbols": split_with_vanilla["symbols"], "items": split_with_vanilla["items"], "essences": split_with_vanilla["essences"], "has_ap_checks": has_ap_checks, "ap_check_in_symbol_pool": ap_check_in_symbol_pool, "next_ap_check": next_ap_check, "active_unlocks": expanded_unlocks, "focused_unlock": focused_unlock, "possible_first_gets": self.possible_first_get_names(), "ap_starting_items": [], "one_per_run_items": ["comfy_pillow"], "safe_modded_icon_ids": True, "item_prompt_lock_fixed_v100": True, "missing_item_all_rarities_v101": True, "strict_tracker_possible_pools_v102": True,
                "goal_floors": self.unlocked_goal_floors_for_mod(), "final_no_mixed_items_v103": True, "missing_item_final_pass_fix_v104": True, "force_from_visible_missing_item_v105": True, "missing_items_and_unlocked_symbols_v106": True, "three_missing_items_unlocked_symbols_fix_v107": True, "tracker_items_and_symbol_fallback_v108": True, "live_symbols_and_three_missing_items_v109": True, "pck_repatch_marker_fix_v110": True, "patch_actual_game_pck_v111": True, "fix_popup_indent_parse_v112": True, "fix_unescaped_dictionary_v113": True, "fix_ap_goal_floors_scope_v114": True, "fix_final_rarity_scope_v115": True, "metadata_only_descriptions_v116": True, "apcheck_single_send_v117": True, "metadata_icons_no_choice_leak_v118": True, "symbol_rarity_gate_v119": True, "symbol_rarity_gate_upgrade_v120": True, "symbol_rarity_gate_all_filters_v121": True, "description_item_icons_v122": True, "all_description_icons_pool_ball_v123": True, "pool_ball_real_target_only_v124": True, "curated_description_icons_no_overflow_v125": True, "pool_ball_unlocked_common_v126": True, "deathlink_debounce_poolball_current_v127": True, "deathlink_no_reflect_retry_v128": True, "deathlink_after_received_fix_v129": True, "reliable_failed_payment_deathlink_v130": True, "deathlink_2s_buffer_v131": True, "deathlink_2s_cooldown_no_delay_v132": True, "deathlink_repeat_cooldown_reset_v133": True, "quiet_received_deathlink_logs_v134": True, "diamond_respects_very_rare_checks_v135": True, "high_rarity_boost_no_common_lock_v136": True, "boost_off_disables_priority_v137": True, "fix_target_kind_parse_v138": True, "filler_buffs_traps_v139": True, "max_filler_checks_200_v142": True, "buff_trap_frequency_tiers_v143": True, "individual_buff_trap_weights_v144": True, "named_buff_trap_weight_options_v145": True, "remove_old_buff_trap_edit_lists_v146": True, "fix_buff_trap_generation_error_v147": True, "remove_old_buff_trap_asdict_keys_v148": True, "ingame_ap_overlay_v149": True, "overlay_effects_start_run_fix_v150": True, "dud_trap_current_run_only_v151": True, "choice_symbols_essence_token_buff_v152": True, "choice_symbols_option_name_v153": True, "fix_overlay_newline_parse_v154": True, "fix_overlay_label_newlines_v155": True, "overlay_real_newlines_v156": True, "overlay_force_real_lines_v157": True, "overlay_no_string_newlines_v158": True, "start_buffs_every_run_v159": True, "start_buffs_exact_once_v160": True, "apcheck_multi_and_strict_checks_v161": True, "force_payment_deathlink_option_v162": True, "fix_slot_string_refresh_v165": True, "apcheck_slot_merge_v163": True, "fix_slot_apcheck_parse_v164": True, "client_command_cleanup_v140": True, "starting_symbol_mode_v141": (self.slot_data or {}).get("starting_symbol_mode", "ap_checks"), "safe_icon_loader_v60": True, "overflow_guard_v62": True, "boost_command_fix_v63": True, "force_repatch_v64": True, "empty_item_pool_fix_v65": True, "empty_symbol_boost_pool_v66": empty_symbol_boost_pool, "empty_item_boost_pool_v67": empty_item_boost_pool, "empty_essence_boost_pool_v68": empty_essence_boost_pool, "ap_check_remove_done_v70": has_ap_checks, "ap_check_keep_symbols_v71": has_ap_checks, "ap_check_real_symbol_release_v72": ap_check_in_symbol_pool, "tracker_items_essences_visible_v78": True, "default_symbols_only_when_no_tracker_symbol_v73": True, "respect_symbol_rarity_v77": True, "fail_payment_log_deathlink_v74": True, "matryoshka_base_only_v75": True, "ap_check_always_while_missing_v75": True, "spin_ap_checks_mode": bool((self.slot_data or {}).get("spin_ap_checks_mode", False)), "unlockable_chance_boost": self._unlockable_chance_boost_enabled(), "unlockable_chance_boost_mode": self._unlockable_chance_boost_mode(), "rare_very_rare_pool": self._rare_very_rare_pool_enabled(), "essence_randomizer_enabled": bool((self.slot_data or {}).get("essence_randomizer_enabled", False)), "easy_content": EASY_CONTENT}, sort_keys=True)
            if not force and signature == self._last_generated_mod_signature:
                return
            self._last_generated_mod_signature = signature

            scripts_path = self.generated_mod_path / "scripts"
            art_path = self.generated_mod_path / "art"
            sfx_path = self.generated_mod_path / "sfx"
            scripts_path.mkdir(parents=True, exist_ok=True)
            art_path.mkdir(parents=True, exist_ok=True)
            sfx_path.mkdir(parents=True, exist_ok=True)
            (self.generated_mod_path / "SELECTME.LBAL").write_text("", encoding="utf-8")

            # Clear old generated scripts/art so old floor/check/unsafe mod icons do not stay around.
            for old in list(scripts_path.glob("*.gd")):
                try:
                    old.unlink()
                except OSError:
                    pass
            unsafe_generated_patterns = ["*2895537308*", "*_STEAM_ID_*", "*__STEAM_ID__*", "*_PACK_*"]
            for pattern in unsafe_generated_patterns:
                for old_file in list(scripts_path.glob(pattern)) + list(art_path.glob(pattern)):
                    try:
                        old_file.unlink()
                    except OSError:
                        pass

            # Generate the AP Check symbol only while AP Check locations are still missing.
            # Once all AP Check locations are checked, remove it from the generated floor
            # pool so low-filler/spin-check runs return to vanilla symbols cleanly.
            if has_ap_checks:
                (scripts_path / "ap_check.gd").write_text(
                    self._build_ap_check_symbol_script(),
                    encoding="utf-8",
                )
                try:
                    image_bytes = pkgutil.get_data(__package__, "ap_check.png")
                    if image_bytes:
                        for art_name in (
                            "ap_check.png",
                            "ap_check_STEAM_ID_777770.png",
                            "ap_check_STEAM_ID_777770_PACK_Archipelago AP.png",
                            "ap_check_STEAM_ID_777770_PACK_Archipelago_AP.png",
                        ):
                            (art_path / art_name).write_bytes(image_bytes)
                except Exception:
                    pass

            # Write built-in easy content-pack scripts so players only need the APWorld/YAML.
            self._write_easy_content_pack_scripts(scripts_path, art_path)

            # Icon-only suits/items for descriptions. These are not added as AP reward targets.
            self._write_suit_description_icon_scripts(scripts_path)
            self._write_item_description_icon_scripts(scripts_path)

            # Only replace the generic missing/? image files with the uploaded red-X.
            self._write_missing_fallback_art_only(art_path)

            # Generic descriptions for the red-X missing placeholders; no per-symbol placeholder scripts.
            self._write_generic_missing_description_scripts(scripts_path)

            # One missing placeholder per rarity so empty rolled rarities do not borrow from other rarities.
            self._write_missing_choice_placeholder_scripts(scripts_path, art_path)

            # Chance boosting is handled by repeating real vanilla/AP types in the
            # generated floor lists above. Do not write ap_boost_* override scripts;
            # LBAL can display those overrides as pink question marks.

            for floor in floors:
                # Use the vanilla floor ID so the game inherits the exact floor
                # text/effects, but limit generated scripts to selected AP floors.
                (scripts_path / f"ap_floor_{floor}.gd").write_text(
                    self._build_ap_floor_script(
                        floor,
                        split_with_vanilla["symbols"],
                        split_with_vanilla["items"],
                        split_with_vanilla["essences"],
                        has_ap_checks,
                        list(self.slot_data.get("symbols", [])),
                        list(self.slot_data.get("items", [])),
                        list(self.slot_data.get("essences", [])),
                        floor_type=f"floor_{floor}",
                        enabled=True,
                        focused_unlock=focused_unlock,
                        empty_symbol_boost_pool=empty_symbol_boost_pool,
                        empty_item_boost_pool=empty_item_boost_pool,
                        empty_essence_boost_pool=empty_essence_boost_pool,
                        ap_check_in_symbol_pool=ap_check_in_symbol_pool,
                    ),
                    encoding="utf-8",
                )

            readme = (
                "Archipelago AP generated mod.\n"
                "Keep the original Steam Luck be a Landlord.pck. Do not replace it.\n"
                "The AP client regenerates these floor/check scripts from ap_state.json.\n"
                "The AP mod page contains AP floors 1-20. Selected AP seed floors get AP Check symbols and the AP unlock pool. Unselected floors are disabled/safe: they show an <icon_dud> warning and do not contain AP Checks or AP unlock items, so restarting on those floors will not grant new AP content. Each AP floor uses the matching regular floor modifier description.\n"
                "The AP client auto-refreshes this mod folder when AP unlocks/checks change.\n"
                "AP Check art stays installed even after all AP Check locations are done, but generated AP floors stop using AP Check starting symbols and fall back to the vanilla floor start.\n"
                "Fixed vanilla internal IDs: Big Symbol Bomb=symbol_bomb_big, Quantum Symbol Bomb=symbol_bomb_quantum, Black Suits=blue_suits, Wealthy Capsule=lucky_capsule, The Tortoise and the Hare=turtle_and_rabbit. Essence randomizer off leaves the vanilla Essence tab untouched; essence randomizer on filters only AP-unlocked essences.\n"
                "If LBAL does not live-reload the already-open choice screen, close/reopen the screen or start a new AP floor run; the Steam .pck should stay original.\n"
            )
            (self.generated_mod_path / "README.txt").write_text(readme, encoding="utf-8")
        except Exception as exc:
            logger.warning("Could not generate LBAL AP mod folder: %s", exc)

    def _overlay_push_line_v149(self, line: str) -> None:
        line = str(line or "").strip()
        if not line:
            return
        if line.startswith("Queued check:"):
            return
        lines = list(getattr(self, "_overlay_recent_client_lines_v149", []) or [])
        if lines and lines[-1] == line:
            return
        lines.append(line)
        self._overlay_recent_client_lines_v149 = lines[-8:]

    def _recent_received_lines_v149(self, limit: int = 6) -> List[str]:
        item_lookup = self.item_id_to_name()
        location_lookup = self.location_id_to_name()
        lines: List[str] = []
        recent_items = list(self.items_received)[-max(1, int(limit)):]
        for network_item in recent_items:
            item_name = self._display_item_name(item_lookup.get(network_item.item, str(network_item.item)))
            player_name = self.player_names.get(network_item.player, str(network_item.player))
            location_name = location_lookup.get(network_item.location, str(network_item.location))
            lines.append(f"Got {item_name} from {player_name}")
        return lines[-limit:]

    def _overlay_effect_count_lines_v150(self) -> List[str]:
        counts = self.ap_effect_counts_v150()
        return [
            "Buffs sent:",
            f"Destroy:{counts.get('Buff: Start With a Destroy Token', 0)}  +$5:{counts.get('Buff: Start With $5', 0)}",
            f"Reroll:{counts.get('Buff: Start With a Reroll Token', 0)}  Essence:{counts.get('Buff: Start With an Essence Token', 0)}",
            f"Big Bomb:{counts.get('Buff: Choice of Symbols', 0)}",
            "Traps sent:",
            f"Half $:{counts.get('Trap: Half Money', 0)}  Pay:{counts.get('Trap: Force Payment', 0)}  Dud:{counts.get('Trap: Add Dud Symbol', 0)}",
        ]

    def _overlay_floors_finished_v149(self) -> Dict[str, Any]:
        goal_floors = [int(f) for f in ((self.slot_data or {}).get("goal_floors", []) or [])]
        if not goal_floors:
            return {"finished": 0, "required": 0, "total": 0, "text": "0/0"}
        checked_names = set(self.checked_location_names()) | set(getattr(self, "_pending_check_names", set()))
        finished_floors: List[int] = []
        for floor in goal_floors:
            if f"Clear Floor {floor} Goal" in checked_names:
                finished_floors.append(floor)
        required = int((self.slot_data or {}).get("floors_required", len(goal_floors)) or len(goal_floors))
        if required <= 0:
            required = len(goal_floors)
        required = max(1, min(required, len(goal_floors)))
        return {
            "finished": len(finished_floors),
            "required": required,
            "total": len(goal_floors),
            "finished_floors": finished_floors,
            "text": f"{len(finished_floors)}/{required}",
        }

    def _overlay_data_v149(self, connected: bool) -> Dict[str, Any]:
        threshold = max(1, int(self.deathlink_send_threshold() or 1))
        current = max(0, int(getattr(self, "_local_death_pending_count", 0) or 0))
        deathlink_remaining = max(1, threshold - current)
        deathlink_text = str(deathlink_remaining)
        if self._deathlink_override is False:
            deathlink_text = "off"
        floors = self._overlay_floors_finished_v149()

        client_lines: List[str] = []
        client_lines.append("AP: connected" if connected else "AP: disconnected")
        if self.auth:
            client_lines.append(f"Slot: {self.auth}")
        next_ap = self._next_unchecked_ap_check_name() if self._has_missing_ap_checks_for_mod() else None
        if next_ap:
            client_lines.append(f"Next: {next_ap}")
        else:
            client_lines.append("AP Checks: done")
        for line in self._recent_received_lines_v149(5):
            client_lines.append(line)
        for line in list(getattr(self, "_overlay_recent_client_lines_v149", []) or [])[-4:]:
            if line not in client_lines:
                client_lines.append(line)

        return {
            "enabled": True,
            "client_lines": client_lines[-10:],
            "deathlink_remaining": deathlink_remaining,
            "deathlink_text": deathlink_text,
            "deathlink_threshold": threshold,
            "deathlink_pending_count": current,
            "floors": floors,
            "right_lines": [
                f"DeathLink in: {deathlink_text}",
                f"Floors done: {floors.get('text', '0/0')}",
                f"Goal floors: {floors.get('total', 0)}",
                "",
                *self._overlay_effect_count_lines_v150(),
            ],
        }

    def write_state_file(self, connected: Optional[bool] = None) -> None:
        if connected is None:
            connected = bool(self.server and self.server.socket and not self.server.socket.closed and self.slot is not None)

        expanded_unlocks = self.expand_unlocks_from_received_items()
        split = split_unlocks(expanded_unlocks)

        # Live bridge fields: the generated LBAL mod folder can only be re-read
        # when LBAL reloads mod data. For true in-run updating, a patched Godot
        # bridge should read these *active* pools from ap_state.json and filter
        # the next Add Symbol / Add Item / Add Essence choice screen directly.
        active_unlocks = self.active_unlocks_for_mod()
        active_split = split_unlocks(active_unlocks)
        # V108: source the live/game targets directly from the tracker's possible
        # Send checks. This makes items like Treasure Map appear as soon as the
        # tracker says Treasure Map is possible, even if older active_unlocks logic
        # would miss it.
        tracker_possible_unlocks = []
        tracker_possible_raw_names: Set[str] = set()
        for check_name in self.possible_first_get_names():
            if isinstance(check_name, str) and check_name.startswith("Send: "):
                tracker_possible_raw_names.add(check_name.removeprefix("Send: "))
        # V124: also trust the current in-logic tracker list. Some Send locations
        # can be shown there instead of possible_first_get_names(), which made
        # Pool Ball show in the tracker but not enter the live Add Item pool.
        for loc_name in self.in_logic_mission_names():
            if not isinstance(loc_name, str):
                continue
            raw_name = loc_name.removeprefix("Send: ") if loc_name.startswith("Send: ") else loc_name
            if raw_name == "Matryoshka Doll" or raw_name in SYMBOLS or raw_name in NORMAL_ITEMS or raw_name in ESSENCES:
                tracker_possible_raw_names.add(raw_name)
        for raw_name in sorted(tracker_possible_raw_names, key=self._natural_sort_key):
            tracker_possible_unlocks.append("Unlock: " + raw_name)
        tracker_possible_split = split_unlocks(tracker_possible_unlocks)
        active_split = tracker_possible_split

        # Keep all received unlocks separately. If there are no symbol Send checks
        # currently in the tracker, Add Symbol should still show already-unlocked
        # AP symbols instead of only defaults/AP Check.
        received_split = split_unlocks([
            unlock for unlock in self.expand_unlocks_from_received_items()
            if (
                unlock.startswith("Unlock: ")
                or unlock.startswith("Unlock Symbol: ")
                or unlock.startswith("Unlock Item: ")
                or unlock.startswith("Unlock Essence: ")
            )
        ])
        active_split_with_vanilla = active_split
        # V127: Pool Ball is not a fallback and should not stay forever just
        # because Unlock: Pool Ball was received. It is only active while the
        # current tracker still has Send: Pool Ball open. Use tracker/display
        # lines too because some current targets are displayed there before they
        # appear in possible_first_get_names().
        closed_v127 = set(self.checked_location_names()) | set(getattr(self, "_pending_check_names", set()))
        for sent_id_v127 in set(getattr(self, "_last_sent_locations", set())):
            sent_name_v127 = self.location_id_to_name().get(sent_id_v127)
            if sent_name_v127:
                closed_v127.add(sent_name_v127)
        tracker_raw_candidates_v127: Set[str] = set()
        for line_v127 in list(self.in_logic_mission_names()) + list(self.tracker_display_lines()):
            if not isinstance(line_v127, str):
                continue
            raw_v127 = line_v127.removeprefix("Send: ").strip()
            if raw_v127 == "Matryoshka Doll" or raw_v127 in SYMBOLS or raw_v127 in NORMAL_ITEMS or raw_v127 in ESSENCES:
                loc_v127 = "Send: " + raw_v127
                if loc_v127 not in closed_v127:
                    tracker_raw_candidates_v127.add(raw_v127)
        if tracker_raw_candidates_v127:
            current_tracker_unlocks_v127 = ["Unlock: " + raw_v127 for raw_v127 in sorted(tracker_raw_candidates_v127, key=self._natural_sort_key)]
            current_tracker_split_v127 = split_unlocks(current_tracker_unlocks_v127)
            for key_v127 in ("symbols", "items", "essences"):
                if current_tracker_split_v127.get(key_v127):
                    active_split_with_vanilla[key_v127] = sorted(set(active_split_with_vanilla.get(key_v127, [])) | set(current_tracker_split_v127[key_v127]), key=self._natural_sort_key)
        goal_floors = [int(f) for f in (self.slot_data.get("goal_floors", []) or [])]

        item_randomizer_enabled = bool((self.slot_data or {}).get("item_randomizer_enabled", True))
        essence_randomizer_enabled = bool((self.slot_data or {}).get("essence_randomizer_enabled", False))
        boost_pool_mode = self._unlockable_chance_boost_enabled() and self._unlockable_chance_boost_mode() != "regular"
        symbol_boost_pool_empty = boost_pool_mode and len(active_split.get("symbols", [])) == 0
        item_boost_pool_empty = boost_pool_mode and len(active_split_with_vanilla.get("items", [])) == 0
        essence_boost_pool_empty = boost_pool_mode and len(active_split.get("essences", [])) == 0

        # V68: boost mode is category-specific. If the tracker only has Essence
        # unlocks possible, Add Symbol/Add Item should fall back to the normal
        # vanilla pools instead of showing Missing AP Symbol/Item placeholders.
        # The category that actually has possible AP content remains locked.
        # V73: keep symbol filtering on even when no AP symbols are currently possible.
        # That makes Add Symbol show only the default starting symbols (and AP Check when active)
        # instead of opening the whole vanilla/slot symbol pool.
        lock_symbols = True
        # V91: Items/Essences must stay AP-filtered too. Otherwise locked vanilla
        # items like Tax Evasion/Treasure Map can leak when only AP Checks or
        # symbols are possible in the tracker.
        lock_normal_items = True
        lock_essences = True

        all_slot_symbols = list(self.slot_data.get("symbols", [])) or list(SYMBOLS)
        all_slot_items = list(self.slot_data.get("items", [])) or list(NORMAL_ITEMS)
        all_slot_essences = list(self.slot_data.get("essences", [])) or list(ESSENCES)

        # V73: symbol pool is strict: tracker-possible symbols only. Default starting symbols
        # are injected separately through always_allowed_symbol_types, so do not fall back to every
        # slot symbol when the current possible symbol list is empty.
        # V106: symbols are tracker-possible first. If there are no symbols in
        # the tracker at all, fall back to already-received AP symbols so unlocked
        # AP symbols do not disappear from Add Symbol.
        if len(active_split_with_vanilla["symbols"]) > 0:
            live_symbols = list(active_split_with_vanilla["symbols"])
        else:
            live_symbols = list(received_split.get("symbols", []))
        live_items = list(active_split_with_vanilla["items"]) if lock_normal_items else all_slot_items
        live_essences = list(active_split_with_vanilla["essences"]) if lock_essences else all_slot_essences

        # V89: AP Add Symbol choices should only allow the real vanilla defaults
        # plus AP Check/tracker-possible symbols. Do NOT include slot_data
        # starting_symbols, because generated/AP slots can put symbols like Crab
        # there and they leak into the Add Symbol pool before being unlocked.
        default_starting_symbol_names = ["Coin", "Flower", "Pearl", "Cherry", "Cat"]
        starting_symbol_names = list(default_starting_symbol_names)
        starting_symbol_types = sorted(self._symbol_types_for_names(starting_symbol_names))
        live_symbol_types = sorted(self._symbol_types_for_names(live_symbols))
        live_item_types = sorted(self._item_types_for_names(live_items))
        live_essence_types = sorted(self._essence_types_for_names(live_essences))
        # V72 priority pools contain only real AP targets currently shown in the tracker.
        # The live PCK can inject these into the rolled choice rarity so possible
        # AP symbols/items/essences are actually selectable immediately.
        priority_symbol_types = sorted(self._symbol_types_for_names(active_split.get("symbols", [])))
        priority_item_types = sorted(self._item_types_for_names(active_split_with_vanilla.get("items", [])))
        priority_essence_types = sorted(self._essence_types_for_names(active_split.get("essences", [])))
        has_ap_checks = self._has_missing_ap_checks_for_mod()
        # V75: AP Check is a tracker/check target too, so keep it available while
        # any AP Check locations remain, even if a real symbol such as Matryoshka
        # is also currently possible. The rest of the pool stays strict: default
        # symbols + tracker-possible symbols only.
        ap_check_symbol_pool_active = has_ap_checks

        data = {
            "live_update_nonce_v109": time.time(),
            "connected": connected,
            "server": self.server_address,
            "slot_name": self.auth,
            "team": self.team,
            "slot": self.slot,
            "game": self.game,
            "bridge_folder": str(self.bridge_path),
            "slot_data": self.slot_data,
            "mod_control": {
                "enabled": True,
                "lock_all_content_until_ap_unlock": True,
                "show_only_allowed_floors": True,
                "give_each_unlock_once": True,
                "use_bundles": bool(self.slot_data.get("item_bundles_enabled", False)),
                "live_update": True,
                "lock_symbols": lock_symbols,
                "symbol_boost_pool_empty": symbol_boost_pool_empty,
                "item_boost_pool_empty": item_boost_pool_empty,
                "essence_boost_pool_empty": essence_boost_pool_empty,
                "boost_pool_mode": boost_pool_mode,
                "boost_enabled": boost_pool_mode,
                "boost_override": self._unlockable_chance_boost_override,
                "has_ap_checks": has_ap_checks,
                "ap_check_priority": ap_check_symbol_pool_active,
                "ap_check_symbol_pool_active": ap_check_symbol_pool_active,
                "lock_normal_items": lock_normal_items,
                "lock_essences": lock_essences,
            },
            "allowed_floors": goal_floors,
            "hidden_floors": [floor for floor in all_floors() if floor not in goal_floors],
            "received_items": self.received_items_for_state(),
            "ap_effects": self.received_ap_effects_for_state_v139(),
            "unlocks": expanded_unlocks,
            "active_unlocks": active_unlocks,
            "received_unlocked_symbols": split["symbols"],
            "received_unlocked_items": split["items"],
            "received_unlocked_essences": split["essences"],
            "unlocked_symbols": live_symbols,
            "unlocked_items": live_items,
            "unlocked_essences": live_essences,
            "unlocked_other": split["other"],
            "vanilla_rarity_pool": self._vanilla_rarity_pool_from_slot(),
            "live_pool": {
                "display_symbols": live_symbols,
                "display_items": live_items,
                "display_essences": live_essences,
                "symbol_types": live_symbol_types,
                "item_types": live_item_types,
                "essence_types": live_essence_types,
                "starting_symbol_types": starting_symbol_types,
                "priority_symbol_types": priority_symbol_types,
                "priority_item_types": priority_item_types,
                "priority_essence_types": priority_essence_types,
                # V92: explicit tracker-category flags. The PCK should not use
                # stale priority/allowed item sets to decide that items are possible
                # when the tracker only contains AP Checks and a symbol such as Crab.
                "strict_tracker_possible_pools_v102": True,
                "has_symbol_targets": len(live_symbols) > 0,
                "symbol_targets_are_received_fallback_v106": len(active_split.get("symbols", [])) == 0 and len(live_symbols) > 0,
                "symbol_targets_are_received_fallback_v108": len(active_split.get("symbols", [])) == 0 and len(live_symbols) > 0,
                "has_item_targets": len(active_split_with_vanilla.get("items", [])) > 0,
                "has_essence_targets": len(active_split.get("essences", [])) > 0,
                "always_allowed_symbol_types": sorted(set(starting_symbol_types) | {"base", "empty", "dud"} | ({"ap_check"} if ap_check_symbol_pool_active else set())),
                "always_allowed_item_types": [],
                "one_per_run_item_types": ["comfy_pillow"],
                "has_ap_checks": has_ap_checks,
                "ap_check_priority": ap_check_symbol_pool_active,
                "ap_check_symbol_pool_active": ap_check_symbol_pool_active,
                "lock_symbols": lock_symbols,
                "symbol_boost_pool_empty": symbol_boost_pool_empty,
                "item_boost_pool_empty": item_boost_pool_empty,
                "essence_boost_pool_empty": essence_boost_pool_empty,
                "boost_pool_mode": boost_pool_mode,
                "lock_normal_items": lock_normal_items,
                "lock_essences": lock_essences,
            },
            "checked_location_ids": sorted(self.checked_locations),
            "checked_location_names": self.checked_location_names(),
            "missing_location_ids": sorted(self.missing_locations),
            "missing_location_names": self.missing_location_names(),
            "tracker_sphere_locations": self.in_logic_mission_names(),
            "possible_first_get_checks": self.possible_first_get_names(),
            "focused_unlock": self._focused_unlock_for_mod(),
            "unlockable_chance_boost": self._unlockable_chance_boost_enabled(),
            "unlockable_chance_boost_override": self._unlockable_chance_boost_override,
            "starting_symbol_mode": str((self.slot_data or {}).get("starting_symbol_mode", "ap_checks")),
            "pending_check_names": sorted(self._pending_check_names, key=self._natural_sort_key),
            "next_ap_check": (self._next_unchecked_ap_check_name() if has_ap_checks else None),
            "deathlink": {
                **(self.slot_data.get("deathlink", {}) or {}),
                "enabled": self.deathlink_enabled(),
                "receive_chance_percent": self.deathlink_receive_chance(),
                "receive_threshold": self.deathlink_receive_threshold(),
                "send_threshold": self.deathlink_send_threshold(),
                "force_payment_trap_counts_deathlink": self.force_payment_trap_counts_deathlink(),
            },
            "deathlink_pending": self.pending_deathlinks,
            "overlay": self._overlay_data_v149(connected),
            "ap_effects": self.ap_effects_from_received_items(),
            "ap_effect_counts": self.ap_effect_counts_v150(),
            "files_the_game_can_write": {
                "checks_to_send.json": {"locations": ["Payment 1", "AP Check 1", "Send: Coin"]},
                "deathlink_send.json": {"cause": "Luck be a Landlord run ended"},
            },
            "updated_at": time.time(),
        }
        # Compatibility fields for simple Godot scripts that expect the older prototype shape.
        data["host"] = self.server_address
        data["items_to_give"] = expanded_unlocks
        data["checks_received"] = len(self.checked_locations)
        data["symbols_to_give"] = split["symbols"]
        data["normal_items_to_give"] = split["items"]
        # Compatibility bridge field for older PCK bridge builds. Use the same
        # active essence pool as live_pool instead of every vanilla essence, so
        # essence_randomizer behaves the same through both code paths.
        data["essences_to_give"] = live_essences
        data["all_essences"] = list(self.slot_data.get("essences", []))

        self.write_effect_files()

        # Main external bridge folder.
        atomic_write_json(self.bridge_path / "ap_state.json", data)
        # Direct Godot user:// mirror, so the game can read user://ap_state.json without custom paths.
        atomic_write_json(self.godot_path / "ap_state.json", data)
        # Also generate a normal LBAL user mod folder from AP unlocks.
        # When AP sends new unlocks or checks are cleared, the mod folder is refreshed.
        auto_mod_sig = json.dumps({
            "unlocks": expanded_unlocks,
            "active_unlocks": active_unlocks,
            "checked": sorted(self.checked_locations),
            "missing": sorted(self.missing_locations),
            "next_ap_check": (self._next_unchecked_ap_check_name() if data.get("live_pool", {}).get("has_ap_checks", False) else None),
            "goal_floors": goal_floors,
            "live_pool": data.get("live_pool", {}),
        }, sort_keys=True)
        force_mod_refresh = auto_mod_sig != self._last_auto_mod_state_signature
        self._last_auto_mod_state_signature = auto_mod_sig
        self.write_generated_lbal_mod(force=force_mod_refresh)

    def ap_effects_from_received_items(self) -> List[Dict[str, Any]]:
        # V150: this used to return [], which overwrote the real ap_effects key
        # in ap_state.json and stopped buff/trap effects from reaching the game.
        return self.received_ap_effects_for_state_v139()


    def _option_value(self, key: str, default: Any = None) -> Any:
        """Read a generated slot option from modern slot_data["options"] or older top-level slot_data."""
        options = self.slot_data.get("options", {}) or {}
        if isinstance(options, dict) and key in options:
            return options.get(key)
        return self.slot_data.get(key, default)

    @staticmethod
    def _truthy_option(value: Any) -> bool:
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
        return bool(value)

    def deathlink_settings(self) -> Dict[str, Any]:
        # Prefer slot_data["options"] for thresholds/chance. Some old generated
        # slot_data also has a nested deathlink dict; if the two disagree, the
        # YAML/options value should win so the client does not show 1/3 when the
        # YAML says deathlink_receive_threshold: 2.
        direct = self.slot_data.get("deathlink", {}) or {}
        options = self.slot_data.get("options", {}) or {}

        enabled_default = self.slot_data.get("deathlink_enabled", False)
        if isinstance(direct, dict) and direct:
            enabled_default = direct.get("enabled", direct.get("deathlink", enabled_default))

        def pick(option_key: str, direct_key: str, fallback: Any) -> Any:
            if isinstance(options, dict) and option_key in options:
                return options.get(option_key)
            if isinstance(direct, dict) and direct_key in direct:
                return direct.get(direct_key)
            if isinstance(direct, dict) and option_key in direct:
                return direct.get(option_key)
            return self.slot_data.get(option_key, fallback)

        return {
            **(direct if isinstance(direct, dict) else {}),
            "enabled": self._truthy_option(pick("deathlink", "enabled", enabled_default)),
            "receive_chance_percent": pick("deathlink_receive_chance", "receive_chance_percent", 100),
            "receive_threshold": pick("deathlink_receive_threshold", "receive_threshold", 1),
            "send_threshold": pick("deathlink_send_threshold", "send_threshold", 1),
        }

    def deathlink_enabled(self) -> bool:
        if self._deathlink_override is not None:
            return bool(self._deathlink_override)
        return bool(self.deathlink_settings().get("enabled", False))

    def deathlink_receive_chance(self) -> int:
        try:
            return max(0, min(100, int(self.deathlink_settings().get("receive_chance_percent", 100))))
        except Exception:
            return 100

    def deathlink_receive_threshold(self) -> int:
        if self._deathlink_receive_threshold_override is not None:
            return max(1, min(20, int(self._deathlink_receive_threshold_override)))
        try:
            return max(1, min(20, int(self.deathlink_settings().get("receive_threshold", 1))))
        except Exception:
            return 1

    def deathlink_send_threshold(self) -> int:
        if self._deathlink_send_threshold_override is not None:
            return max(1, min(20, int(self._deathlink_send_threshold_override)))
        try:
            return max(1, min(20, int(self.deathlink_settings().get("send_threshold", 1))))
        except Exception:
            return 1

    def force_payment_trap_counts_deathlink(self) -> bool:
        """Whether Force Payment trap deaths count toward outgoing DeathLink."""
        return self._truthy_option(self._option_value("force_payment_trap_counts_deathlink", True))

    def _consume_force_payment_trap_deathlink_marker_v162(self) -> bool:
        """Return True once when a fresh Force Payment trap marker is present."""
        paths = [self.bridge_path / "force_payment_trap_active.json", self.godot_path / "force_payment_trap_active.json"]
        now = time.time()
        fresh = False
        for path in paths:
            try:
                if not path.exists():
                    continue
                data = read_json(path, {})
                created = float(data.get("created_at", data.get("time", 0)) or 0) if isinstance(data, dict) else 0.0
                # One Force Payment trap should only suppress one nearby failed-payment death.
                if created > 0 and now - created <= 180.0:
                    fresh = True
                delete_if_exists(path)
            except Exception:
                try:
                    delete_if_exists(path)
                except Exception:
                    pass
        return fresh

    async def update_deathlink_tag(self, force_enable: bool = False) -> None:
        enabled = self.deathlink_enabled() or bool(force_enable)
        tags = set(getattr(self, "tags", set()) or set())
        changed = False
        if enabled and "DeathLink" not in tags:
            tags.add("DeathLink")
            changed = True
        elif not enabled and "DeathLink" in tags:
            tags.discard("DeathLink")
            changed = True
        self.tags = tags
        if changed and self.server and self.slot is not None:
            await self.send_msgs([{ "cmd": "ConnectUpdate", "tags": sorted(tags) }])

    async def send_death(self, cause: str = "Luck be a Landlord run ended", force: bool = False) -> None:
        if not force and not self.deathlink_enabled() and "DeathLink" not in getattr(self, "tags", set()):
            logger.info("DeathLink is not enabled for this slot; not sending death.")
            return
        if self.server is None or self.slot is None:
            logger.info("Cannot send DeathLink before connecting to an Archipelago room.")
            return

        # Make outgoing DeathLink reliable. Some rooms/servers only route
        # DeathLink correctly after this client has advertised the DeathLink tag.
        self.tags = set(getattr(self, "tags", set()) or set())
        tag_changed = "DeathLink" not in self.tags
        self.tags.add("DeathLink")
        if tag_changed:
            await self.send_msgs([{ "cmd": "ConnectUpdate", "tags": sorted(self.tags) }])
            await asyncio.sleep(0.1)

        payload = {
            "time": time.time(),
            "source": self.player_names.get(self.slot, self.auth or getattr(self, "player_name", None) or "Luck be a Landlord"),
            "cause": cause or "Luck be a Landlord run ended",
        }
        await self.send_msgs([{ "cmd": "Bounce", "tags": ["DeathLink"], "data": payload }])
        logger.info("Sent DeathLink: %s", payload["cause"])

    async def send_game_deathlink(self, cause: str = "Failed to pay rent in Luck be a Landlord") -> None:
        """Send a DeathLink that came from the patched LBAL game bridge."""
        # Treat the active AP DeathLink tag as enabled too. This keeps outgoing
        # DeathLinks working if old slot_data/client settings parsed stale but
        # the server already has this client tagged for DeathLink.
        if self._deathlink_override is False:
            logger.info("LBAL requested DeathLink send, but DeathLink was explicitly disabled with /deathlink off.")
            return
        if self.server is None or self.slot is None:
            self._pending_local_deathlink_cause_v128 = cause or "Failed to pay rent in Luck be a Landlord"
            logger.info("Queued LBAL local DeathLink until AP room is connected: %s", self._pending_local_deathlink_cause_v128)
            return
        if not self.deathlink_enabled() and "DeathLink" not in getattr(self, "tags", set()):
            # V71: a game-created deathlink_send.json means the patched game reached
            # the failed-rent branch. Force the outgoing tag/payload unless the user
            # explicitly disabled DeathLink with /deathlink off. This fixes stale or
            # incomplete slot_data preventing sends.
            logger.info("LBAL requested DeathLink send while slot_data showed DeathLink off; forcing outgoing DeathLink.")
        threshold = self.deathlink_send_threshold()
        self._local_death_pending_count += 1
        if self._local_death_pending_count < threshold:
            logger.info("Local LBAL death %s/%s before sending DeathLink.", self._local_death_pending_count, threshold)
            return
        self._local_death_pending_count = 0
        self.local_death_counter += 1
        await self.send_death(cause or "Failed to pay rent in Luck be a Landlord", force=True)


    def queue_received_deathlink_for_game(self, data: Dict[str, Any]) -> None:
        nonce = str(data.get("time", time.time())) + "_" + str(data.get("source", "unknown"))
        if nonce == self._last_deathlink_nonce:
            return
        self._last_deathlink_nonce = nonce
        payload = {
            "enabled": True,
            "nonce": nonce,
            "source": str(data.get("source", "another player")),
            "cause": str(data.get("cause", "DeathLink received")),
            "received_at": time.time(),
            "action": "end_run",
        }
        self._overlay_push_line_v149("Received DeathLink")
        self.pending_deathlinks.append(payload)
        self.pending_deathlinks = self.pending_deathlinks[-5:]
        # V129: only suppress the immediate game-over caused by this received
        # DeathLink. Do not block a later normal failed-payment death in the next
        # run. The run-log filter also ignores explicit DeathLink game-over lines.
        self._recent_received_deathlink_gameover_until_v128 = time.time() + 2.5
        for path in getattr(self, "_deathlink_receive_paths", []):
            atomic_write_json(path, payload)
        self.write_state_file()

    def handle_local_death_from_game(self, cause: str) -> None:
        cause = cause or "Failed to pay rent in Luck be a Landlord"
        if not self.force_payment_trap_counts_deathlink() and self._consume_force_payment_trap_deathlink_marker_v162():
            logger.info("Force Payment trap death ignored for outgoing DeathLink due to force_payment_trap_counts_deathlink=false.")
            self._local_deathlink_buffer_cause_v131 = None
            self._local_deathlink_buffer_deadline_v131 = 0.0
            return
        suppress_until_v128 = float(getattr(self, "_recent_received_deathlink_gameover_until_v128", 0.0) or 0.0)
        if time.time() < suppress_until_v128:
            cause_low_v129 = str(cause or "").lower()
            explicit_rent_failure_v129 = (
                "failed to pay" in cause_low_v129
                or "could not pay" in cause_low_v129
                or "cannot pay" in cause_low_v129
                or "rent is late" in cause_low_v129
                or "evicted" in cause_low_v129
                or "bankrupt" in cause_low_v129
            )
            if not explicit_rent_failure_v129:
                # V134: the same received-DeathLink game-over can be noticed by
                # several hooks. Do not spam the client chat/log with repeated
                # no-reflect messages.
                now_no_reflect_v134 = time.time()
                last_no_reflect_v134 = float(getattr(self, "_last_no_reflect_log_time_v134", 0.0) or 0.0)
                if now_no_reflect_v134 - last_no_reflect_v134 >= 5.0:
                    logger.info("LBAL game over was caused by a received DeathLink; not sending an outgoing DeathLink to avoid reflect/loops.")
                    self._last_no_reflect_log_time_v134 = now_no_reflect_v134
                self._recent_received_deathlink_gameover_until_v128 = 0.0
                return
            logger.info("LBAL failed-rent death happened after a received DeathLink; sending outgoing DeathLink immediately: %s", cause)
            self._recent_received_deathlink_gameover_until_v128 = 0.0

        now = time.time()
        key = str(cause).strip().lower() or "failed to pay rent in luck be a landlord"
        last_time = float(getattr(self, "_last_local_deathlink_event_time_v127", 0.0) or 0.0)
        cooldown = float(getattr(self, "_local_deathlink_cooldown_seconds_v132", 2.0) or 2.0)
        if now - last_time < cooldown:
            logger.info("Suppressed duplicate LBAL local DeathLink within %.1f-second cooldown: %s", cooldown, cause)
            return
        self._last_local_deathlink_event_key_v127 = key
        self._last_local_deathlink_event_time_v127 = now
        self._local_deathlink_buffer_cause_v131 = None
        self._local_deathlink_buffer_deadline_v131 = 0.0
        logger.info("Sending LBAL local DeathLink immediately; duplicate triggers suppressed for %.1f seconds: %s", cooldown, cause)
        Utils.async_start(self.send_game_deathlink(cause), name="Luck DeathLink from local failed-payment death")

    async def _flush_local_deathlink_buffer_v131(self) -> None:
        # V132 compatibility: old scheduled buffer tasks, if any, should not delay
        # or send anything. New local deaths are handled immediately by
        # handle_local_death_from_game(), with only a 2-second duplicate cooldown.
        self._local_deathlink_buffer_cause_v131 = None
        self._local_deathlink_buffer_deadline_v131 = 0.0
        return

    def clear_deathlink_ack_files(self) -> None:
        for path in getattr(self, "_deathlink_ack_paths", []):
            delete_if_exists(path)

    def write_effect_files(self) -> None:
        data = {"effects": [], "updated_at": time.time()}
        atomic_write_json(self.bridge_path / "ap_effects.json", data)
        atomic_write_json(self.godot_path / "ap_effects.json", data)

    def log_new_received_items(self) -> None:
        """Kept for compatibility; received items are already shown by Archipelago itself."""
        self._last_received_count = len(self.received_items_for_state())

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            self.slot_data = args.get("slot_data", {}) or {}
            # V88: clear stale files from a previous client/game run so reconnecting
            # does not immediately submit old Floor Payment checks.
            for stale_path in [
                self.bridge_path / "checks_to_send.json",
                self.godot_path / "checks_to_send.json",
            ]:
                try:
                    delete_if_exists(stale_path)
                except Exception:
                    pass
            self._run_state_seen_signatures_v88.clear()
            self._run_state_initialized_v88 = False
            self._client_started_at_v88 = time.time()
            Utils.async_start(self.update_deathlink_tag(), name="Luck DeathLink tag update")
            self._overlay_push_line_v149("Connected to Archipelago")
            self.write_state_file(connected=True)
            # Silently regenerate the generated Luck be a Landlord mod folder
            # whenever the slot connects. No output is printed here.
            self.write_generated_lbal_mod(force=True)
            Utils.async_start(self.flush_pending_checks(), name="flush pending Luck checks")
            if self._pending_local_deathlink_cause_v128:
                pending_cause_v128 = self._pending_local_deathlink_cause_v128
                self._pending_local_deathlink_cause_v128 = None
                self.handle_local_death_from_game(pending_cause_v128)

        elif cmd == "ReceivedItems":
            self.write_state_file()
            if self._required_floor_goals_checked_or_pending() and self._raspberry_goal_ready():
                self._pending_client_goal_status = True
                Utils.async_start(self.flush_pending_checks(), name="flush pending Luck goal after Raspberry")

        elif cmd == "RoomUpdate":
            self.write_state_file()

        elif cmd == "Bounced":
            tags = set(args.get("tags", []) or [])
            data = args.get("data", {}) or {}
            if "DeathLink" in tags and isinstance(data, dict):
                self.on_deathlink(data)

    def _deathlink_event_key(self, data: Dict[str, Any]) -> str:
        """Stable key for deduping incoming DeathLink Bounce packets."""
        source = str(data.get("source", ""))
        cause = str(data.get("cause", ""))
        event_time = str(data.get("time", ""))
        if event_time or source or cause:
            return f"{event_time}|{source}|{cause}"
        try:
            return json.dumps(data, sort_keys=True, default=str)
        except Exception:
            return str(data)

    def _deathlink_event_seen(self, data: Dict[str, Any]) -> bool:
        key = self._deathlink_event_key(data)
        if key in self._seen_deathlink_event_keys:
            return True
        self._seen_deathlink_event_keys.add(key)
        self._seen_deathlink_event_order.append(key)
        if len(self._seen_deathlink_event_order) > 100:
            old_key = self._seen_deathlink_event_order.pop(0)
            self._seen_deathlink_event_keys.discard(old_key)
        return False

    def on_deathlink(self, data: Dict[str, Any]) -> None:
        if not self.deathlink_enabled() and "DeathLink" not in getattr(self, "tags", set()):
            return
        source = str(data.get("source", ""))
        own_names = {str(self.auth or ""), str(getattr(self, "player_name", "") or "")}
        try:
            own_names.add(str(self.player_names.get(self.slot, "")))
        except Exception:
            pass
        if source and source in own_names:
            return
        if self._deathlink_event_seen(data):
            return
        self._incoming_death_pending_count += 1
        threshold = self.deathlink_receive_threshold()
        if self._incoming_death_pending_count < threshold:
            logger.info("Received DeathLink %s/%s before applying it.", self._incoming_death_pending_count, threshold)
            return
        self._incoming_death_pending_count = 0
        chance = self.deathlink_receive_chance()
        if chance <= 0:
            logger.info("Ignored received DeathLink because receive chance is 0%%.")
            return
        if chance < 100 and random.randint(1, 100) > chance:
            logger.info("Received DeathLink did not trigger due to receive chance %s%%.", chance)
            return
        self.received_deathlink_counter += 1
        # V134: avoid chat spam if the same incoming DeathLink is queued more than
        # once by reconnect/replay or duplicate event metadata.
        cause_v134 = str(data.get("cause", "DeathLink received"))
        now_queue_v134 = time.time()
        last_queue_v134 = float(getattr(self, "_last_received_deathlink_queue_log_time_v134", 0.0) or 0.0)
        last_cause_v134 = str(getattr(self, "_last_received_deathlink_queue_log_cause_v134", ""))
        if cause_v134 != last_cause_v134 or now_queue_v134 - last_queue_v134 >= 5.0:
            logger.info("Queueing received DeathLink for LBAL game: %s", cause_v134)
            self._last_received_deathlink_queue_log_time_v134 = now_queue_v134
            self._last_received_deathlink_queue_log_cause_v134 = cause_v134
        self.queue_received_deathlink_for_game(data)

    def load_run_log_offsets(self) -> None:
        self._run_log_offsets = {}
        try:
            data = read_json(self._run_log_offsets_path, {})
            if isinstance(data, dict):
                self._run_log_offsets = {str(k): int(v) for k, v in data.items()}
        except Exception:
            self._run_log_offsets = {}

    def save_run_log_offsets(self) -> None:
        try:
            atomic_write_json(self._run_log_offsets_path, self._run_log_offsets)
        except Exception:
            pass

    def _candidate_run_log_files(self) -> List[Path]:
        candidates: List[Path] = []
        names = [
            "run_log.txt",
            "run_logs.txt",
            "run_log.json",
            "run_logs.json",
            "ap_run_log.txt",
            "ap_log.txt",
        ]
        for base in [self.bridge_path, self.godot_path, self.generated_mod_path]:
            for name in names:
                candidates.append(base / name)
        for folder in [self.bridge_path / "run_logs", self.godot_path / "run_logs"]:
            if folder.exists():
                candidates.extend(sorted(folder.glob("*.txt")))
                candidates.extend(sorted(folder.glob("*.log")))
                candidates.extend(sorted(folder.glob("*.json")))
        # Keep unique paths in order.
        seen: Set[str] = set()
        unique: List[Path] = []
        for path in candidates:
            key = str(path)
            if key not in seen:
                seen.add(key)
                unique.append(path)
        return unique

    def _lines_from_log_text(self, text: str) -> List[str]:
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [str(entry) for entry in data]
            if isinstance(data, dict):
                for key in ("lines", "logs", "entries", "events"):
                    value = data.get(key)
                    if isinstance(value, list):
                        return [json.dumps(entry) if isinstance(entry, (dict, list)) else str(entry) for entry in value]
                return [json.dumps(data)]
        except Exception:
            pass
        return text.splitlines()

    def _iter_new_run_log_lines(self) -> List[str]:
        lines: List[str] = []
        changed = False
        for path in self._candidate_run_log_files():
            try:
                if not path.exists() or not path.is_file():
                    continue
                key = str(path)
                raw = path.read_text(encoding="utf-8", errors="ignore")
                all_lines = self._lines_from_log_text(raw)

                if key not in self._run_log_offsets:
                    # First time seeing this log: mark current end and skip it.
                    # This stops old run logs from instantly sending every AP Check.
                    self._run_log_offsets[key] = len(all_lines)
                    changed = True
                    continue

                old_offset = int(self._run_log_offsets.get(key, 0))
                # If the log was truncated/rewritten, start at the new end instead
                # of replaying the whole file.
                if old_offset < 0 or old_offset > len(all_lines):
                    self._run_log_offsets[key] = len(all_lines)
                    changed = True
                    continue

                new_lines = all_lines[old_offset:]
                if new_lines:
                    lines.extend(new_lines)
                self._run_log_offsets[key] = len(all_lines)
                changed = True
            except Exception:
                continue
        if changed:
            self.save_run_log_offsets()
        return lines

    def load_pending_checks(self) -> None:
        # Do not replay stale queued checks from an older client/mod version.
        # Checks are queued live from this point forward and saved after queueing.
        self._pending_check_names = set()
        for path in getattr(self, "_pending_check_paths", []):
            try:
                delete_if_exists(path)
            except Exception:
                pass

    def save_pending_checks(self) -> None:
        data = {"locations": sorted(self._pending_check_names, key=self._natural_sort_key)}
        for path in getattr(self, "_pending_check_paths", []):
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                atomic_write_json(path, data)
            except Exception:
                pass

    def _floor_payment_check_allowed_v67(self, name: str) -> bool:
        match = re.fullmatch(r"Floor (\d+) Payment (\d+)", str(name))
        if not match:
            return True
        floor = int(match.group(1))
        unlocked = {int(f) for f in self.unlocked_goal_floors_for_mod()}
        if unlocked and floor not in unlocked:
            # V87: silently drop locked-floor payment checks. The game/PCK can
            # repeatedly report its current visual floor, and printing every
            # rejected Floor X Payment Y floods the AP client chat/log.
            return False
        return True

    def queue_checks(self, check_names: Iterable[str]) -> None:
        name_to_id = self.location_name_to_id()
        checked = set(self.checked_location_names())
        sent_ids = set(getattr(self, "_last_sent_locations", set()))
        for name in check_names:
            if (
                isinstance(name, str)
                and name in name_to_id
                and name not in checked
                and name_to_id[name] not in sent_ids
                and self._floor_payment_check_allowed_v67(name)
            ):
                self._pending_check_names.add(name)
        self.save_pending_checks()

    async def flush_pending_checks(self) -> None:
        if not self._pending_check_names and not getattr(self, "_pending_client_goal_status", False):
            return
        if not self.server or self.slot is None:
            self.save_pending_checks()
            return

        name_to_id = self.location_name_to_id()
        checked = set(self.checked_location_names())
        send_names = [
            name for name in sorted(self._pending_check_names, key=self._natural_sort_key)
            if name in name_to_id and name not in checked
        ]
        pending_goal = bool(getattr(self, "_pending_client_goal_status", False))
        if not send_names and not pending_goal:
            self._pending_check_names.clear()
            self.save_pending_checks()
            return

        messages: List[Dict[str, Any]] = []
        if send_names:
            messages.append({
                "cmd": "LocationChecks",
                "locations": [name_to_id[name] for name in send_names],
            })
        if getattr(self, "_pending_client_goal_status", False):
            messages.append({"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL})

        sent_location_ids: List[int] = []
        if send_names:
            sent_location_ids = [name_to_id[name] for name in send_names]

        if messages:
            await self.send_msgs(messages)

        # Keep the live mod in sync immediately after AP Check locations are sent.
        # AP's RoomUpdate can arrive a moment later; this local sent cache stops
        # AP Check from staying in the Add Symbol pool after the final one was
        # already submitted.
        if sent_location_ids:
            self._last_sent_locations.update(sent_location_ids)

        for name in send_names:
            self._pending_check_names.discard(name)
        self._pending_client_goal_status = False
        self.save_pending_checks()
        if sent_location_ids:
            self.write_state_file()

    def _extract_coin_totals_from_line(self, line: str) -> List[int]:
        """Return real current money totals from one LBAL run-log line.

        Strict on purpose: do not parse "Gained X coins this spin" as a total.
        """
        values: List[int] = []
        patterns = [
            r"\bcurrently have\s+(-?\d+)\s+coins?\b",
            r"\bcoin total is now\s+(-?\d+)(?:\s+after spinning)?\b",
            r"\byou now have\s+(-?\d+)\s+coins?\b",
            r"\bnow have\s+(-?\d+)\s+coins?\b",
        ]
        low = line.lower()
        for pattern in patterns:
            for match in re.finditer(pattern, low, re.IGNORECASE):
                try:
                    values.append(int(match.group(1)))
                except (ValueError, IndexError):
                    pass
        out: List[int] = []
        for value in values:
            if value not in out:
                out.append(value)
        return out


    def _location_name_considered_done(self, name: str) -> bool:
        """True when a location is already checked, pending to send, or just sent."""
        if name in set(self.checked_location_names()):
            return True
        if name in getattr(self, "_pending_check_names", set()):
            return True
        loc_id = self.location_name_to_id().get(name)
        if loc_id is not None and loc_id in set(getattr(self, "_last_sent_locations", set())):
            return True
        return False

    def _per_floor_payment_checks_enabled(self) -> bool:
        slot = self.slot_data or {}
        return bool(slot.get("per_floor_payment_checks") or slot.get("payment_check_style") == "per_floor")

    def _current_floor_from_bridge_state(self) -> Optional[int]:
        """Read the current LBAL floor written by the patched PCK."""
        for path in [self.bridge_path / "lbal_run_state.json", self.godot_path / "lbal_run_state.json"]:
            try:
                if not path.exists():
                    continue
                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                floor = int(data.get("floor", 0))
                if 1 <= floor <= 20:
                    return floor
            except Exception:
                continue
        return None

    def _active_payment_floor(self) -> Optional[int]:
        floors = self.unlocked_goal_floors_for_mod()
        unlocked = {int(f) for f in floors}
        floor = self._current_floor_from_bridge_state()
        if floor is not None:
            # V82: if the player is sitting on a selected AP floor that has not
            # been unlocked yet, do not show/send that floor's payment checks.
            if int(floor) in unlocked:
                return int(floor)
            return int(floors[0]) if floors else None
        if floors:
            return int(floors[0])
        if self._floor_unlock_mode_from_slot_v67() == "unlock_through_items":
            return None
        goal_floors = self.slot_data.get("goal_floors", []) if self.slot_data else []
        if goal_floors:
            try:
                return int(goal_floors[0])
            except Exception:
                pass
        return None

    def _all_main_payments_done_for_goal(self, floor: Optional[int] = None) -> bool:
        """Floor clear checks should only appear/send after the correct Payment 12 is done."""
        name_to_id = self.location_name_to_id()
        if self._per_floor_payment_checks_enabled():
            active_floor = int(floor or self._active_payment_floor() or 1)
            for payment in range(1, 13):
                name = f"Floor {active_floor} Payment {payment}"
                if name in name_to_id and not self._location_name_considered_done(name):
                    return False
            return True

        for payment in range(1, 13):
            name = f"Payment {payment}"
            if name in name_to_id and not self._location_name_considered_done(name):
                return False
        return True

    def _floor_goal_is_unlocked_and_ready(self, floor: int) -> bool:
        """The clear goal is visible/sent only for unlocked floors after all payments."""
        if not self._all_main_payments_done_for_goal(floor):
            return False
        unlocked = set(int(f) for f in (self.unlocked_goal_floors_for_mod() or []))
        goal_floors = [int(f) for f in (self.slot_data.get("goal_floors", []) or [])]
        if not unlocked and goal_floors:
            unlocked.add(goal_floors[0])
        return int(floor) in unlocked

    def _floor_goal_names_for_victory(self) -> List[str]:
        """Return the floor-goal check(s) to send for a VICTORY log line.

        LBAL's run log only prints plain "VICTORY" and usually does not include
        the apartment floor number.  In multi-floor AP seeds, use the lowest
        selected/unlocked floor whose clear check is still missing.  This makes
        normal progression work automatically instead of ignoring the victory.
        """
        missing = set(self.missing_location_names())
        checked = set(self.checked_location_names())
        goal_floors = sorted({int(f) for f in (self.slot_data.get("goal_floors", []) or []) if 1 <= int(f) <= 20})
        if not goal_floors:
            return []

        if not self._all_main_payments_done_for_goal():
            return []

        out: List[str] = []
        for floor in goal_floors:
            if not self._floor_goal_is_unlocked_and_ready(floor):
                continue
            name = f"Clear Floor {floor} Goal"
            if name in missing and name not in checked:
                out.append(name)
                break
        return out

    def _mark_goal_status_if_enough_floors_cleared(self, newly_detected: Iterable[str]) -> None:
        goal_floors = sorted({int(f) for f in (self.slot_data.get("goal_floors", []) or []) if 1 <= int(f) <= 20})
        if not goal_floors:
            self._pending_client_goal_status = True
            return
        required = int(self.slot_data.get("goal_floors_required", len(goal_floors)) or len(goal_floors))
        required = max(1, min(required, len(goal_floors)))
        cleared = set(name for name in self.checked_location_names() if name.startswith("Clear Floor "))
        cleared.update(name for name in newly_detected if isinstance(name, str) and name.startswith("Clear Floor "))
        if len(cleared) >= required and self._raspberry_goal_ready():
            self._pending_client_goal_status = True

    def _detect_payment_from_coin_total(self, line: str, detected_names: Set[str]) -> None:
        """Send Payment only when a rent-sized drop happens while Payment is the current mission.

        LBAL's run log normally shows payment as:
        "Coin total is now 38 after spinning" then next spin "Currently have 13 coins".
        There is no "paid rent" text, so this detects that drop while avoiding:
        - old logs on startup
        - new run starts
        - game over/failure text
        - small item/shop losses
        """
        low = line.lower()

        if "--- starting run" in low:
            self._last_seen_coin_total = None
            return

        blocked_words = [
            "game over", "failure", "failed", "rent is late", "evicted",
            "being evicted", "late and you are", "could not pay", "cannot pay",
            "did not pay", "insufficient", "bankrupt",
        ]
        if any(word in low for word in blocked_words):
            self._last_seen_coin_total = None
            return

        totals = self._extract_coin_totals_from_line(line)
        if not totals:
            return

        is_currently_have_line = "currently have" in low or "you now have" in low or "now have" in low

        for total in totals:
            previous = self._last_seen_coin_total
            self._last_seen_coin_total = total
            if previous is None:
                continue

            drop = previous - total
            if drop < 10:
                continue

            # Only count drops on the next-spin "Currently have" style line.
            # This prevents "gained coins" and most normal updates from becoming payments.
            if not is_currently_have_line:
                continue

            missing = set(self.missing_location_names())
            checked = set(self.checked_location_names())
            for mission in self.in_logic_mission_names():
                if mission.startswith("Payment ") and mission not in self._payment_checks_sent_from_money_drop:
                    detected_names.add(mission)
                    self._payment_checks_sent_from_money_drop.add(mission)
                    break
                m = re.fullmatch(r"Floor (\d+) Payment (\d+)", mission)
                if m and mission not in self._payment_checks_sent_from_money_drop:
                    detected_names.add(mission)
                    self._payment_checks_sent_from_money_drop.add(mission)
                    break

    def _next_unchecked_payment_location_names(self) -> List[str]:
        """Return the lowest missing payment location for the current payment style."""
        missing = set(self.missing_location_names())
        checked = set(self.checked_location_names())

        active_floor = self._active_payment_floor()
        for payment in range(1, 13):
            if self._per_floor_payment_checks_enabled():
                if active_floor is None:
                    candidates = sorted(
                        [name for name in missing if re.fullmatch(rf"Floor \d+ Payment {payment}", name)],
                        key=self._natural_sort_key,
                    )
                else:
                    candidates = [f"Floor {int(active_floor)} Payment {payment}"]
                for mission in candidates:
                    if mission in self._payment_checks_sent_from_money_drop:
                        continue
                    if mission in missing and mission not in checked:
                        return [mission]
            else:
                mission = f"Payment {payment}"
                if mission in self._payment_checks_sent_from_money_drop:
                    continue
                if mission in missing and mission not in checked:
                    return [mission]
        return []

    def _detect_payment_from_add_item_screen(self, line: str, detected_names: Set[str]) -> None:
        """Send exactly one payment check each time the Add Item screen appears.

        After sending, wait for a gained-coins/spin line before arming again.
        This matches fast Comfy Pillow play: click pillow -> payment succeeds ->
        Add Item appears -> send next payment check -> next spin/gained coins
        re-arms the detector for the following payment.
        """
        low = line.lower()

        if "--- starting run" in low or "starting run" in low:
            self._payment_add_item_armed = True
            return

        # Re-arm only once the player has left the add-item/payment flow and a
        # normal spin has paid out.  Match several common log spellings.
        gained_coin_line = (
            "gained coins" in low
            or re.search(r"\bgained\s+[-+]?\d+\s+coins?\b", low)
            or re.search(r"\bcoins?\s+gained\b", low)
            or "after spinning" in low
        )
        if gained_coin_line:
            self._payment_add_item_armed = True
            return

        add_item_line = (
            "add item" in low
            or "add_item" in low
            or "adding item" in low
            or "added item" in low
            or "added items" in low
            or re.search(r"\badded\s+item\s*:", low)
            or "choose an item" in low
            or "choose item" in low
            or "item choice" in low
        )
        if not add_item_line or not self._payment_add_item_armed:
            return

        names = self._next_unchecked_payment_location_names()
        if not names:
            return

        for name in names:
            detected_names.add(name)
            if name.startswith("Payment ") or re.fullmatch(r"Floor \d+ Payment \d+", name):
                self._payment_checks_sent_from_money_drop.add(name)

        self._payment_add_item_armed = False

    def _payment_location_name_for_number_v85(self, payment_index: int, floor: Optional[int] = None) -> Optional[str]:
        """Return the correct AP payment location name for shared/per-floor seeds."""
        try:
            n = int(payment_index)
        except Exception:
            return None
        if n < 1 or n > 12:
            return None
        if self._per_floor_payment_checks_enabled():
            active_floor = int(floor or self._active_payment_floor() or 0)
            if active_floor <= 0:
                return None
            return f"Floor {active_floor} Payment {n}"
        return f"Payment {n}"

    def _queue_payment_progress_v85(self, paid_count: int, detected_names: Set[str], floor: Optional[int] = None) -> None:
        """Queue every missing payment up to paid_count for the active floor/style."""
        try:
            paid_count = max(0, min(12, int(paid_count)))
        except Exception:
            return
        if paid_count <= 0:
            return

        missing = set(self.missing_location_names())
        checked = set(self.checked_location_names())
        for index in range(1, paid_count + 1):
            name = self._payment_location_name_for_number_v85(index, floor)
            if (
                name
                and name in missing
                and name not in checked
                and name not in self._payment_checks_sent_from_money_drop
                and self._floor_payment_check_allowed_v67(name)
            ):
                detected_names.add(name)
                self._payment_checks_sent_from_money_drop.add(name)

    def _detect_payment_progress_from_line(self, line: str, detected_names: Set[str]) -> None:
        """Detect paid rent by payment progress.

        V85: works for both shared Payment N and per-floor Floor X Payment N.
        It catches lines such as "Payments: 7/12", "payment_count: 7", or
        "Payment 7 paid" and sends all missing payment checks up to that number.
        """
        low = line.lower()
        blocked_words = [
            "game over", "failure", "failed", "rent is late", "evicted",
            "being evicted", "late and you are", "could not pay", "cannot pay",
            "did not pay", "insufficient", "bankrupt",
        ]
        if any(word in low for word in blocked_words):
            return

        paid_count: Optional[int] = None
        floor_num: Optional[int] = None

        floor_match = re.search(r"\bfloor\s*(\d+)\b", low, re.IGNORECASE)
        if floor_match:
            try:
                floor_num = int(floor_match.group(1))
            except ValueError:
                floor_num = None

        # Most useful form from run info / state dumps.
        for pat in [
            r"payments?\s*[:=]\s*(\d+)\s*/\s*(\d+)",
            r"rent_payments?\s*[:=]\s*(\d+)\s*/\s*(\d+)",
            r"payments_paid\s*[:=]\s*(\d+)",
            r"current_payment\s*[:=]\s*(\d+)",
            r"payment_count\s*[:=]\s*(\d+)",
            r'"payments_paid"\s*:\s*(\d+)',
            r'"payment"\s*:\s*(\d+)',
        ]:
            match = re.search(pat, low, re.IGNORECASE)
            if match:
                try:
                    paid_count = int(match.group(1))
                    break
                except ValueError:
                    pass

        # Text form after actually paying a bill.
        if paid_count is None and any(word in low for word in ["paid", "paying", "payed"]):
            match = re.search(r"(?:rent\s*)?payment\s*(\d+)", low, re.IGNORECASE)
            if match:
                try:
                    paid_count = int(match.group(1))
                except ValueError:
                    paid_count = None

        if paid_count is None:
            return

        # If this is a per-floor seed, progress can reset per floor. Track the
        # key by floor instead of globally; for shared payments use floor 0.
        key_floor = int(floor_num or self._active_payment_floor() or 0) if self._per_floor_payment_checks_enabled() else 0
        previous = self._last_seen_run_state_payment_by_floor.get(key_floor, 0)
        if paid_count <= previous and paid_count <= self._last_seen_payment_progress:
            return
        self._last_seen_run_state_payment_by_floor[key_floor] = max(previous, paid_count)
        self._last_seen_payment_progress = max(self._last_seen_payment_progress, paid_count)

        self._queue_payment_progress_v85(paid_count, detected_names, key_floor if key_floor else None)

    def _detect_payment_from_run_state_v85(self, detected_names: Set[str]) -> None:
        """Read lbal_run_state.json directly and queue paid payments.

        V88: do not replay stale state from before this AP client connected. On
        first sight of existing lbal_run_state files, mark them as seen and wait
        for a newer nonce/mtime written by the running game.
        """
        current_signatures: Set[str] = set()
        for path in [self.bridge_path / "lbal_run_state.json", self.godot_path / "lbal_run_state.json"]:
            try:
                if not path.exists():
                    continue
                stat = path.stat()
                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                if not isinstance(data, dict):
                    continue
                nonce = str(data.get("nonce", "")) or f"{stat.st_mtime_ns}"
                signature = f"{path}:{nonce}:{stat.st_mtime_ns}"
                current_signatures.add(signature)

                # Startup guard: the first existing state file is usually from an
                # old run. Do not send Floor 1 Payment 1-11 just because the client
                # was restarted/reconnected.
                if not self._run_state_initialized_v88:
                    continue
                if signature in self._run_state_seen_signatures_v88:
                    continue
                # If the file is older than this client process, it is stale.
                try:
                    if stat.st_mtime < self._client_started_at_v88 - 0.25:
                        self._run_state_seen_signatures_v88.add(signature)
                        continue
                except Exception:
                    pass

                self._run_state_seen_signatures_v88.add(signature)
                self._last_seen_run_state_nonce = nonce
                paid_count = int(data.get("payments_paid", data.get("payment", 0)) or 0)
                floor = int(data.get("floor", self._active_payment_floor() or 0) or 0)
                if self._per_floor_payment_checks_enabled():
                    unlocked = {int(f) for f in self.unlocked_goal_floors_for_mod()}
                    if floor not in unlocked:
                        floor = int(self._active_payment_floor() or 0)
                if paid_count > 0:
                    self._queue_payment_progress_v85(paid_count, detected_names, floor if floor > 0 else None)
            except Exception:
                continue

        if not self._run_state_initialized_v88:
            self._run_state_seen_signatures_v88.update(current_signatures)
            self._run_state_initialized_v88 = True

    def _maybe_send_deathlink_from_game_over_log(self, line: str) -> None:
        """Fallback outgoing DeathLink when LBAL logs a normal failed-payment game over.

        The PCK normally writes deathlink_send.json. Some LBAL builds skip the
        exact Pop-up hook, but run logs still show the same GAME OVER that the
        receive-side code forces. This uses that receive-side game-over evidence
        to trigger the normal outgoing DeathLink send path.
        """
        low = str(line or "").lower()
        failed_game_over = (
            "game over" in low
            or "failed to pay" in low
            or "could not pay" in low
            or "cannot pay" in low
            or "rent is late" in low
            or "evicted" in low
            or "bankrupt" in low
        )
        if not failed_game_over:
            return
        # Do not bounce received DeathLinks back out. Receiving a DeathLink writes
        # GAME OVER - DeathLink to the log, and that should stay receive-only.
        if "victory" in low:
            return
        if "deathlink" in low or "death link" in low:
            # V134: only print the no-reflect message once every few seconds;
            # multiple LBAL hooks/log lines can report the same received DeathLink.
            now_no_reflect_v134 = time.time()
            last_no_reflect_v134 = float(getattr(self, "_last_no_reflect_log_time_v134", 0.0) or 0.0)
            if now_no_reflect_v134 - last_no_reflect_v134 >= 5.0:
                logger.info("LBAL game over was caused by a received DeathLink; not sending an outgoing DeathLink to avoid reflect/loops.")
                self._last_no_reflect_log_time_v134 = now_no_reflect_v134
            return
        explicit_rent_failure_v129 = (
            "failed to pay" in low
            or "could not pay" in low
            or "cannot pay" in low
            or "rent is late" in low
            or "evicted" in low
            or "bankrupt" in low
        )
        if time.time() < getattr(self, "_recent_received_deathlink_gameover_until_v128", 0.0) and not explicit_rent_failure_v129:
            now_no_reflect_v134 = time.time()
            last_no_reflect_v134 = float(getattr(self, "_last_no_reflect_log_time_v134", 0.0) or 0.0)
            if now_no_reflect_v134 - last_no_reflect_v134 >= 5.0:
                logger.info("Ignored immediate generic LBAL GAME OVER after a received DeathLink; not reflecting it.")
                self._last_no_reflect_log_time_v134 = now_no_reflect_v134
            return
        if explicit_rent_failure_v129:
            self._recent_received_deathlink_gameover_until_v128 = 0.0
        # V133: do not permanently remember identical GAME OVER text. LBAL can log
        # the exact same failed-rent line on later runs, and the 2-second local
        # cooldown already suppresses duplicate hooks from the same death.
        logger.info("Detected LBAL failed-payment GAME OVER from run log; sending DeathLink.")
        self.handle_local_death_from_game("Failed to pay rent in Luck be a Landlord")

    def _ap_check_destroy_count_from_line_v163(self, line: str) -> int:
        """Return how many AP Check symbols an aggregated destroy log line represents.

        Some LBAL/Godot logs collapse several identical AP Check self-destroy effects
        into one line, e.g. "8 AP Check ... destroyed".  Older client code treated
        that as one AP Check.  This keeps one-check behavior for normal lines but
        sends multiple sequential AP Check locations when a count is visible.
        """
        low = str(line or "").lower()
        candidates: List[int] = []
        patterns = [
            r"(\d+)\s*(?:x\s*)?(?:ap[_\- ]?checks?|ap checks?)",
            r"(?:ap[_\- ]?checks?|ap checks?)\s*(?:x|count|qty|quantity|amount)?\s*[:=]?\s*(\d+)",
            r"(?:destroyed|removed)\s+(\d+)\s+(?:symbols?|tiles?)",
            r"(?:count|qty|quantity|amount)\s*[:=]\s*(\d+)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, low, re.IGNORECASE):
                try:
                    value = int(match.group(1))
                except Exception:
                    continue
                if 1 <= value <= 50:
                    candidates.append(value)
        # If the log repeats ap_check several times in one line, count those too.
        occurrences = len(re.findall(r"(?:ap[_\- ]?check|ap check)", low, re.IGNORECASE))
        if occurrences > 1:
            candidates.append(min(occurrences, 50))
        return max(candidates) if candidates else 1

    def detect_checks_from_run_logs(self) -> Set[str]:
        """Detect checks from new LBAL run-log lines.

        AP Check is strict: it only counts if the line includes AP Check/ap_check
        and a destroy/remove action. This prevents Add Symbol menu previews from
        sending checks.

        First-Get and Payment checks are best-effort because LBAL's logs can vary
        between versions/mod loaders. They only fire from NEW log lines and only
        if the matching AP location is still missing.
        """
        detected_names: Set[str] = set()
        lines = self._iter_new_run_log_lines()
        if not lines:
            return detected_names

        missing = set(self.missing_location_names())
        checked = set(self.checked_location_names())

        symbol_pattern = re.compile(r"(?:ap_check(?:_[a-z0-9_]+)?|ap check)", re.IGNORECASE)
        action_pattern = re.compile(r"(?:destroy|destroyed|remov|removed)", re.IGNORECASE)
        reserved: Set[str] = set()

        possible_first_gets = self.possible_first_get_names()
        # Longest first so names like Black Pepper match before Pepper.
        # LBAL logs usually use internal ids like swear_jar/red_suits, not display names.
        first_get_pairs: List[tuple[str, List[str]]] = []
        for check_name in possible_first_gets:
            if ": " not in check_name:
                continue
            display_name = check_name.split(": ", 1)[1]
            if display_name in SYMBOLS:
                internal = _display_to_lbal_type(display_name, "symbol")
            elif display_name in NORMAL_ITEMS:
                internal = _display_to_lbal_type(display_name, "item")
            else:
                internal = _display_to_lbal_type(display_name, "essence")
            variants = {display_name.lower(), internal.lower(), internal.lower().replace("_", " ")}

            # Extra aliases for LBAL logs that sometimes use shortened effect names.
            # Do not alias Black Suits directly to Clubs/Spades, because that would
            # false-send the item check just from seeing those symbols before the
            # Black Suits item is actually owned. The normal black_suits/giver line
            # is enough once the item exists.
            extra_aliases = {
                "The Tortoise and the Hare": {"tortoise_and_the_hare", "the_tortoise_and_the_hare", "tortoise", "hare"},
                "Big Symbol Bomb": {"symbol_bomb_big", "big_symbol_bomb", "big symbol bomb"},
                "Quantum Symbol Bomb": {"symbol_bomb_quantum", "quantum_symbol_bomb", "quantum symbol bomb"},
                "Wealthy Capsule": {"lucky_capsule", "wealthy_capsule", "wealthy capsule"},
                "Black Suits": {"blue_suits", "black_suits", "black suits"},
                "Red Suits": {"red_suits", "red suits"},
                "Small Symbol Bomb": {"symbol_bomb_small", "small_symbol_bomb", "small symbol bomb"},
                "Small Symbol Bomb Essence": {"symbol_bomb_small_essence", "small_symbol_bomb_essence", "small symbol bomb essence"},
                "Big Symbol Bomb Essence": {"symbol_bomb_big_essence", "big_symbol_bomb_essence", "big symbol bomb essence"},
                "Very Big Symbol Bomb Essence": {"symbol_bomb_very_big_essence", "very_big_symbol_bomb_essence", "very big symbol bomb essence"},
                "Black Suits Essence": {"blue_suits_essence", "black_suits_essence", "black suits essence"},
                "The Tortoise and the Hare Essence": {"turtle_and_rabbit_essence", "the_tortoise_and_the_hare_essence", "tortoise and the hare essence"},
                "Fish Tank Essence": {"fish_bowl_essence", "fish_tank_essence", "fish tank essence", "fish bowl essence"},
                "Kyle the Kernite": {"kyle_the_kernite", "kyle", "kyle the kernite"},
                "Kyle the Kernite Essence": {"kyle_the_kernite_essence", "kyle_essence", "kyle the kernite essence"},
            }.get(display_name, set())
            variants.update(extra_aliases)
            variants = sorted(variants, key=len, reverse=True)
            first_get_pairs.append((check_name, variants))
        first_get_pairs.sort(key=lambda pair: max(len(v) for v in pair[1]), reverse=True)
        first_get_action = re.compile(r"(?:added symbols|added item|destroyed item|\badded\b|\bobtained\b|\bgot\b|\breceived\b|\bdestroyed\b)", re.IGNORECASE)

        for line in lines:
            low = line.lower()

            # V74 outgoing DeathLink fallback: use normal game-over log evidence
            # to send DeathLink when the failed-payment PCK hook was missed.
            self._maybe_send_deathlink_from_game_over_log(line)

            # V161: do not infer Payment checks from log text. The PCK hook sends
            # payment checks only from the successful rent-payment branch.
            # This prevents false Floor Payment sends from stale/current run text.

            # AP Check detection: only count the self-destroy effect line.
            # This avoids double-sending from value_bonus/comparison lines and
            # avoids Add Symbol menu previews that include the word destroyed.
            is_ap_check_destroy = (
                symbol_pattern.search(line)
                and re.search(r'value_to_change\s*:\s*destroyed|"value_to_change"\s*:\s*"destroyed"', line, re.IGNORECASE)
                and re.search(r'effect_type\s*:\s*self|"effect_type"\s*:\s*"self"', line, re.IGNORECASE)
            )
            if is_ap_check_destroy:
                ap_check_count_v163 = self._ap_check_destroy_count_from_line_v163(line)
                for _ap_check_idx_v163 in range(max(1, min(50, ap_check_count_v163))):
                    next_name = self._next_unchecked_ap_check_name(reserved | detected_names)
                    if next_name:
                        reserved.add(next_name)
                        detected_names.add(next_name)
                continue

            # First Get detection for unlocked normal content. Do not trigger from
            # generic AP server text; this is only reading local game run_logs.
            #
            # Some LBAL items/symbols do not always get an explicit "Added item:"
            # or "Added symbols:" line. Examples include Black Suits/Red Suits
            # and symbol-bomb style items, which may only appear in inventory/effect
            # lines such as "Items before effects are:" or "giver:black_suits".
            # Treat any new run-log evidence of an unlocked item/symbol as enough
            # for its First Get check. This is still safe because this loop only
            # reads the local LBAL run log, not Archipelago server text.
            for check_name, display_variants in first_get_pairs:
                if check_name in missing and check_name not in checked and first_get_action.search(line) and any(v in low for v in display_variants):
                    detected_names.add(check_name)
                    break

            # Victory detection. LBAL writes a clean "VICTORY" line at the end
            # of a completed run. Older builds only handled this when the seed had
            # exactly one goal floor; multi-floor seeds were ignored because the
            # log does not include a floor number.  Send the next selected/unlocked
            # floor clear instead, which matches normal AP floor progression.
            if "victory" in low:
                goal_names = self._floor_goal_names_for_victory()
                for goal_name in goal_names:
                    if goal_name in missing and goal_name not in checked:
                        detected_names.add(goal_name)
                if goal_names:
                    self._mark_goal_status_if_enough_floors_cleared(goal_names)
                continue

            # Payment checks are intentionally not sent from plain rent/email text.
            # They send from Add Item, coin drop, payment progress, or direct run state.

        # V161: disabled direct lbal_run_state payment inference. Actual paid
        # payments are queued by the PCK's successful rent-payment hook.
        return detected_names

    def detect_ap_checks_from_run_logs(self) -> Set[str]:
        # Backwards-compatible method name used by older code paths.
        return self.detect_checks_from_run_logs()



def _regular_floor_text(floor: int) -> str:
    """English text matching the normal LBAL floor descriptions for floors 1-20."""
    floor = max(1, min(20, int(floor)))

    floor_lines = {
        1: ["No modifiers."],
        2: ["Rent payment 7 costs <icon_coin>25 more."],
        3: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
        ],
        4: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
        ],
        5: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You start the game with 1 <icon_dud>.",
        ],
        6: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You start the game with 1 <icon_dud>.",
        ],
        7: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You start the game with 2 <icon_dud>.",
        ],
        8: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You start the game with 2 <icon_dud>.",
        ],
        9: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You start the game with 2 <icon_dud>.",
        ],
        10: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You start the game with 2 <icon_dud>.",
            "<icon_dud> is added every 25 spins before rent payment 12.",
        ],
        11: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You start the game with 2 <icon_dud>.",
            "<icon_dud> is added every 25 spins before rent payment 12.",
            "Your landlord has 250 more HP.",
        ],
        12: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 25 spins before rent payment 12.",
            "Your landlord has 250 more HP.",
        ],
        13: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 25 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
        ],
        14: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 20 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
        ],
        15: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 20 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
            "Your landlord uses more challenging fine print.",
        ],
        16: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You receive 1 essence token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 20 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
            "Your landlord uses more challenging fine print.",
        ],
        17: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You receive 1 essence token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 20 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
            "Your landlord uses 2x more fine print.",
            "Your landlord uses more challenging fine print.",
        ],
        18: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 9 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You receive 1 essence token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 20 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
            "Your landlord uses 2x more fine print.",
            "Your landlord uses more challenging fine print.",
        ],
        19: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 9 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You receive 1 essence token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 15 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
            "Your landlord uses 2x more fine print.",
            "Your landlord uses more challenging fine print.",
        ],
        20: [
            "Rent payment 7 costs <icon_coin>25 more.",
            "Rent payment 8 costs <icon_coin>25 more.",
            "Rent payment 9 costs <icon_coin>25 more.",
            "Rent payment 10 costs <icon_coin>25 more.",
            "Rent payment 11 costs <icon_coin>25 more.",
            "You receive 1 removal token less from emails.",
            "You receive 1 reroll token less from emails.",
            "You receive 1 essence token less from emails.",
            "You start the game with 3 <icon_dud>.",
            "<icon_dud> is added every 15 spins before rent payment 12.",
            "Your landlord has 750 more HP.",
            "Your landlord uses 3x more fine print.",
            "Your landlord uses more challenging fine print.",
        ],
    }

    return "\n".join(floor_lines[floor])

def _regular_floor_tokens(floor: int):
    floor = int(floor)
    if floor >= 16:
        return (1, 1, 1)
    if floor >= 9:
        return (1, 1, 2)
    if floor >= 4:
        return (2, 1, 2)
    return (2, 2, 2)

def _regular_floor_effect_values(floor: int) -> Dict[str, Any]:
    """Gameplay values for the normal LBAL floor modifiers.

    The generated AP floor must set these, not just copy the text, otherwise
    effects like starting Duds / less tokens from emails do not actually happen.
    """
    floor = max(1, min(20, int(floor)))
    duds_by_floor = {
        5: 1, 6: 1, 7: 1,
        8: 2, 9: 2, 10: 2, 11: 2, 12: 2, 13: 2, 14: 2, 15: 2,
        16: 3, 17: 3, 18: 3, 19: 3, 20: 3,
    }
    landlord_hp = 750
    if 14 <= floor <= 18:
        landlord_hp = 1000
    elif floor >= 19:
        landlord_hp = 1500

    fine_print_multiplier = 1
    if floor == 18:
        fine_print_multiplier = 2
    elif floor >= 20:
        fine_print_multiplier = 3

    return {
        "starting_duds": duds_by_floor.get(floor, 0),
        "dud_timer": 15 if floor >= 12 else 0,
        "landlord_hp": landlord_hp,
        "landlord_max_hp": landlord_hp,
        "fine_print_multiplier": fine_print_multiplier,
    }

async def game_watcher(ctx: LuckContext):
    checks_files = [ctx.bridge_path / "checks_to_send.json", ctx.godot_path / "checks_to_send.json"]
    deathlink_send_files = [ctx.bridge_path / "deathlink_send.json", ctx.godot_path / "deathlink_send.json"]
    deathlink_ack_files = [ctx.bridge_path / "deathlink_ack.json", ctx.godot_path / "deathlink_ack.json"]

    while not ctx.exit_event.is_set():
        try:
            ctx.write_state_file()

            name_to_id = ctx.location_name_to_id()
            await ctx.flush_pending_checks()

            for checks_file in checks_files:
                if not checks_file.exists():
                    continue
                try:
                    if checks_file.stat().st_mtime < getattr(ctx, "_client_started_at_v88", 0) - 0.25:
                        delete_if_exists(checks_file)
                        continue
                except Exception:
                    pass
                data = read_json(checks_file, {})
                raw_locations = data.get("locations", data if isinstance(data, list) else [])
                if isinstance(data, dict):
                    # V161: PCK can send an AP Check count when many AP Check symbols
                    # destroy in the same spin. Expand it here so each one becomes
                    # the next unchecked AP Check location.
                    try:
                        ap_check_count_v161 = int(data.get("ap_check_next_count", 0) or 0)
                    except Exception:
                        ap_check_count_v161 = 0
                    if ap_check_count_v161 > 0:
                        raw_locations = list(raw_locations) + ["ap_check_next"] * max(0, min(200, ap_check_count_v161))
                check_nonce = ""
                if isinstance(data, dict):
                    check_nonce = str(data.get("nonce", "") or "")
                if check_nonce:
                    seen_nonces = getattr(ctx, "_seen_game_check_nonces_v117", set())
                    if check_nonce in seen_nonces:
                        delete_if_exists(checks_file)
                        continue
                    seen_nonces.add(check_nonce)
                    # Keep the set bounded for long client sessions.
                    if len(seen_nonces) > 512:
                        ctx._seen_game_check_nonces_v117 = set(list(seen_nonces)[-256:])
                    else:
                        ctx._seen_game_check_nonces_v117 = seen_nonces
                check_names: Set[str] = set()
                unknown: List[Any] = []
                for entry in raw_locations:
                    if isinstance(entry, str) and entry.strip().lower() in {"ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"}:
                        next_name = ctx._next_unchecked_ap_check_name(check_names)
                        if next_name:
                            check_names.add(next_name)
                    elif isinstance(entry, str) and entry in name_to_id:
                        check_names.add(entry)
                    elif isinstance(entry, int):
                        lookup = ctx.location_id_to_name()
                        if entry in lookup:
                            check_names.add(lookup[entry])
                        else:
                            unknown.append(entry)
                    elif isinstance(entry, str) and entry.isdigit():
                        lookup = ctx.location_id_to_name()
                        entry_id = int(entry)
                        if entry_id in lookup:
                            check_names.add(lookup[entry_id])
                        else:
                            unknown.append(entry)
                    else:
                        unknown.append(entry)

                if unknown:
                    logger.warning("Unknown Luck be a Landlord checks from game: %s", unknown)

                if check_names:
                    if any(isinstance(entry, str) and entry.strip().lower() in {"ap_check_next", "next_ap_check", "ap check next", "ap check", "ap_check"} for entry in raw_locations):
                        ctx._recent_ap_check_next_request_v117 = time.time()
                    ctx.queue_checks(check_names)
                    await ctx.flush_pending_checks()
                delete_if_exists(checks_file)

            detected_check_names = ctx.detect_ap_checks_from_run_logs()
            # V117: when the Slot Icon patch directly queued AP_CHECK_NEXT, do not
            # also count the same AP Check from the run_log self-destroy line.
            if getattr(ctx, "_recent_ap_check_next_request_v117", 0.0) and time.time() - ctx._recent_ap_check_next_request_v117 < 1.0:
                detected_check_names = {name for name in detected_check_names if not re.fullmatch(r"AP Check \d+", str(name))}
            if detected_check_names:
                ctx.queue_checks(detected_check_names)
                await ctx.flush_pending_checks()

            for death_file in deathlink_send_files:
                if not death_file.exists():
                    continue
                payload = read_json(death_file, {})
                cause = "Failed to pay rent in Luck be a Landlord"
                nonce = ""
                if isinstance(payload, dict):
                    cause = str(payload.get("cause", cause))
                    nonce = str(payload.get("nonce", ""))
                if not nonce:
                    try:
                        nonce = f"{death_file}:{death_file.stat().st_mtime_ns}"
                    except Exception:
                        nonce = f"{death_file}:{time.time()}"
                # V133: process every new bridge file. Some LBAL hooks can reuse
                # the same nonce/text on later deaths; handle_local_death_from_game()
                # now owns the 2-second duplicate cooldown.
                ctx._last_local_deathlink_send_nonce = nonce
                logger.info("Detected LBAL deathlink_send.json from game: %s", cause)
                ctx.handle_local_death_from_game(cause)
                for send_file in deathlink_send_files:
                    delete_if_exists(send_file)
                break

            for ack_file in deathlink_ack_files:
                if not ack_file.exists():
                    continue
                delete_if_exists(ack_file)
                for receive_file in getattr(ctx, "_deathlink_receive_paths", []):
                    delete_if_exists(receive_file)
                ctx.pending_deathlinks.clear()
                ctx.write_state_file()


        except Exception as exc:
            logger.exception("Error in Luck be a Landlord game watcher: %s", exc)

        await asyncio.sleep(0.25)


async def main(parsed_args):
    ensure_ap_check_art_files()
    restore_pck_on_exit = False

    if auto_patch_lbal_pck is not None:
        try:
            patch_status = auto_patch_lbal_pck(get_bridge_path())
            if patch_status.get("backup_warning"):
                logger.warning("LBAL PCK backup warning: %s", patch_status.get("backup_warning"))
            if patch_status.get("patched"):
                restore_pck_on_exit = True
                logger.info("Installed LBAL AP live PCK patch to: %s", patch_status.get("pck_path"))
                logger.info("Backup folder: %s", patch_status.get("backup_folder") or patch_status.get("backup_path"))
            elif patch_status.get("already_patched"):
                restore_pck_on_exit = True
                logger.info("LBAL AP live PCK patch already installed at: %s", patch_status.get("pck_path"))
                logger.info("Backup folder: %s", patch_status.get("backup_folder") or patch_status.get("backup_path"))
            elif patch_status.get("error"):
                logger.warning("LBAL PCK patch was not installed: %s", patch_status.get("error"))
        except Exception as exc:
            logger.warning("LBAL PCK patch failed: %s", exc)

    ctx = None
    watcher = None
    try:
        ctx = LuckContext(parsed_args.connect, parsed_args.password)
        ctx.auth = parsed_args.name
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

        if gui_enabled and not getattr(parsed_args, "nogui", False):
            ctx.run_gui()
        ctx.run_cli()

        watcher = asyncio.create_task(game_watcher(ctx), name="LuckBeALandlordGameWatcher")
        await ctx.exit_event.wait()
    finally:
        if ctx is not None:
            ctx.server_address = None
            if watcher is not None:
                watcher.cancel()
            try:
                await ctx.shutdown()
            except Exception as exc:
                logger.warning("Luck client shutdown warning: %s", exc)

        # V42: when the user closes the client window with X, restore the original
        # game PCK from the backup automatically. This cannot run if Windows kills
        # the process or the PC loses power, but it works for normal GUI/CLI close.
        if restore_pck_on_exit and restore_original_lbal_pck is not None:
            try:
                restore_status = restore_original_lbal_pck(get_bridge_path())
                if restore_status.get("restored"):
                    logger.info("Restored original LBAL PCK on client close: %s", restore_status.get("pck_path"))
                elif restore_status.get("error"):
                    logger.warning("Could not restore original LBAL PCK on close: %s", restore_status.get("error"))
            except Exception as exc:
                logger.warning("Could not restore original LBAL PCK on close: %s", exc)


def launch(*args: str) -> None:
    parser = get_base_parser(description="Luck be a Landlord Archipelago Client")
    parser.add_argument("--name", default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")
    parsed_args = parser.parse_args(args)
    parsed_args = handle_url_arg(parsed_args, parser=parser)

    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(main(parsed_args))
    colorama.deinit()


if __name__ == "__main__":
    launch(*sys.argv[1:])
